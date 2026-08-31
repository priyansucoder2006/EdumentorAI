from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.learning_progress import LearningProgress
from app.models.assessment import Assessment
from app.schemas.progress import RecommendationItem
from app.ai.agents.recommender_agent import RecommenderAgent
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[RecommendationItem])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_progress = db.query(LearningProgress).filter(LearningProgress.user_id == current_user.id).all()
    recent_assessment = db.query(Assessment).filter(Assessment.user_id == current_user.id).order_by(Assessment.created_at.desc()).first()

    weak = [p.concept for p in all_progress if p.mastery_score < 50.0]
    strong = [p.concept for p in all_progress if p.mastery_score >= 75.0]
    overall_mastery = (sum(p.mastery_score for p in all_progress) / len(all_progress)) if all_progress else 70.0

    recommender = RecommenderAgent()
    recs = recommender.generate_recommendations(
        topic="Newton's Laws of Motion",
        overall_mastery=overall_mastery,
        weak_concepts=weak,
        strong_concepts=strong,
        misconceptions=[]
    )
    return recs
