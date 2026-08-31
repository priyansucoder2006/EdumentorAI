import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
import motor.motor_asyncio
from app.core.config import settings
from app.core.logging import logger

_sync_client: Optional[MongoClient] = None
_async_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None


def get_mongo_client() -> Optional[MongoClient]:
    """
    Returns or initializes the singleton synchronous PyMongo client connected to MongoDB Atlas.
    """
    global _sync_client
    if _sync_client is None:
        try:
            _sync_client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB Atlas: {e}")
            _sync_client = None
    return _sync_client


def get_async_mongo_client() -> Optional[motor.motor_asyncio.AsyncIOMotorClient]:
    """
    Returns or initializes the singleton asynchronous Motor client connected to MongoDB Atlas.
    """
    global _async_client
    if _async_client is None:
        try:
            _async_client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
        except Exception as e:
            logger.warning(f"Could not connect to async MongoDB Atlas: {e}")
            _async_client = None
    return _async_client


def get_mongo_db() -> Optional[Database]:
    """
    Returns the target MongoDB database instance or None if connection is unavailable.
    """
    client = get_mongo_client()
    if client is not None:
        try:
            return client[settings.MONGODB_DB_NAME]
        except Exception as e:
            logger.warning(f"Could not access MongoDB database '{settings.MONGODB_DB_NAME}': {e}")
            return None
    return None


def init_mongodb() -> bool:
    """
    Validates connection to MongoDB Atlas and creates required indexes for tenant isolation & performance.
    """
    try:
        client = get_mongo_client()
        if client:
            client.admin.command('ping')
            db = client[settings.MONGODB_DB_NAME]

            # Index users collection by email and user_id
            db.users.create_index("email", unique=True)
            db.users.create_index("id", unique=True)

            # Index learner_profiles collection by user_id
            db.learner_profiles.create_index("user_id", unique=True)

            # Index lessons, interactions, documents, and progress by user_id for tenant isolation
            db.lessons.create_index("user_id")
            db.interactions.create_index([("user_id", pymongo.ASCENDING), ("lesson_id", pymongo.ASCENDING)])
            db.documents.create_index("user_id")
            db.learning_progress.create_index([("user_id", pymongo.ASCENDING), ("topic", pymongo.ASCENDING)])
            db.audit_logs.create_index([("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])

            logger.info("Successfully connected to MongoDB Atlas & initialized collections/indexes.")
            return True
    except Exception as e:
        logger.warning(f"MongoDB Atlas initialization notice: {e}")
        return False


class MongoSyncService:
    """
    Provides data syncing and tenant-scoped document retrieval for MongoDB Atlas.
    """

    @staticmethod
    def sync_user(user_data: Dict[str, Any]):
        try:
            db = get_mongo_db()
            if db is not None:
                doc = {
                    "id": user_data.get("id"),
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "preferred_language": user_data.get("preferred_language", "en"),
                    "education_level": user_data.get("education_level", "beginner"),
                    "last_synced_at": datetime.now(timezone.utc)
                }
                db.users.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
        except Exception as e:
            logger.warning(f"Failed to sync user to MongoDB Atlas: {e}")

    @staticmethod
    def sync_profile(user_id: str, profile_data: Dict[str, Any]):
        try:
            db = get_mongo_db()
            if db is not None:
                doc = {
                    "user_id": user_id,
                    **profile_data,
                    "updated_at": datetime.now(timezone.utc)
                }
                db.learner_profiles.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
        except Exception as e:
            logger.warning(f"Failed to sync profile to MongoDB Atlas: {e}")

    @staticmethod
    def log_auth_event(user_id: str, email: str, event_type: str, status: str = "success"):
        try:
            db = get_mongo_db()
            if db is not None:
                db.audit_logs.insert_one({
                    "user_id": user_id,
                    "email": email,
                    "event_type": event_type,
                    "status": status,
                    "timestamp": datetime.now(timezone.utc)
                })
        except Exception as e:
            logger.warning(f"Failed to record auth audit log in MongoDB Atlas: {e}")

    @staticmethod
    def sync_interaction(user_id: str, lesson_id: str, interaction_data: Dict[str, Any]):
        try:
            db = get_mongo_db()
            if db is not None:
                doc = {
                    "user_id": user_id,
                    "lesson_id": lesson_id,
                    **interaction_data,
                    "timestamp": datetime.now(timezone.utc)
                }
                db.interactions.insert_one(doc)
        except Exception as e:
            logger.warning(f"Failed to sync interaction to MongoDB Atlas: {e}")
