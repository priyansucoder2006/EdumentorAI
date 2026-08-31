from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.mongodb import MongoSyncService
from app.models.user import User
from app.models.learner_profile import LearnerProfile
from app.schemas.auth import UserRegister, UserLogin, UserResponse, Token
from app.schemas.learner import LearnerProfileResponse, LearnerProfileUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        preferred_language=user_in.preferred_language,
        education_level=user_in.education_level
    )
    db.add(user)
    db.flush()

    # Create associated learner profile
    profile = LearnerProfile(
        user_id=user.id,
        knowledge_level=user_in.education_level if user_in.education_level in ["beginner", "intermediate", "advanced"] else "beginner",
        preferred_language=user_in.preferred_language,
        available_time=20
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    # Sync to MongoDB Atlas
    MongoSyncService.sync_user({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "education_level": user.education_level
    })
    MongoSyncService.sync_profile(user.id, {
        "knowledge_level": profile.knowledge_level,
        "preferred_language": profile.preferred_language,
        "available_time": profile.available_time
    })
    MongoSyncService.log_auth_event(user.id, user.email, "register", "success")

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        MongoSyncService.log_auth_event("anonymous", user_in.email, "login_failed", "invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    # Sync to MongoDB Atlas & log auth event
    MongoSyncService.sync_user({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "education_level": user.education_level
    })
    MongoSyncService.log_auth_event(user.id, user.email, "login", "success")

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    MongoSyncService.log_auth_event(current_user.id, current_user.email, "logout", "success")
    return {"success": True, "message": "Logged out successfully."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/profile", response_model=LearnerProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    if not profile:
        profile = LearnerProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/profile", response_model=LearnerProfileResponse)
def update_profile(
    profile_in: LearnerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    if not profile:
        profile = LearnerProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    # Sync updated profile to MongoDB Atlas
    MongoSyncService.sync_profile(current_user.id, {
        "knowledge_level": profile.knowledge_level,
        "learning_goal": profile.learning_goal,
        "preferred_depth": profile.preferred_depth,
        "available_time": profile.available_time,
        "learning_style": profile.learning_style,
        "preferred_language": profile.preferred_language,
        "strong_topics": profile.strong_topics,
        "weak_topics": profile.weak_topics
    })

    return profile
