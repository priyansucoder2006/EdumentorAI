import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.learner_profile import LearnerProfile
from app.core.security import get_password_hash

# Use isolated test database
TEST_DB_URL = "sqlite:///./test_edumentor.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_edumentor.db"):
        try:
            os.remove("./test_edumentor.db")
        except Exception:
            pass


@pytest.fixture(scope="function")
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client, db_session):
    # Create or fetch test user
    user = db_session.query(User).filter(User.email == "test_teacher@edumentor.ai").first()
    if not user:
        user = User(
            name="Test Teacher",
            email="test_teacher@edumentor.ai",
            password_hash=get_password_hash("password123"),
            preferred_language="hinglish",
            education_level="beginner"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    res = client.post("/api/auth/login", json={"email": "test_teacher@edumentor.ai", "password": "password123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
