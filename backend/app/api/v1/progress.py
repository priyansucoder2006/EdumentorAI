from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.learning_progress import LearningProgress
from app.models.learning_path import LearningPath
from app.schemas.progress import (
    MasteryOverviewResponse,
    ConceptMasteryItem,
    LearningPathResponse
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=MasteryOverviewResponse)
def get_overall_mastery(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_progress = db.query(LearningProgress).filter(LearningProgress.user_id == current_user.id).all()
    
    if not all_progress:
        return MasteryOverviewResponse(
            overall_mastery=0.0,
            total_topics_studied=0,
            total_concepts_learned=0,
            strong_topics=[],
            weak_topics=[],
            concept_details=[]
        )

    topics_set = {p.topic for p in all_progress}
    avg_mastery = sum(p.mastery_score for p in all_progress) / len(all_progress)
    strong = [p.concept for p in all_progress if p.mastery_score >= 75.0]
    weak = [p.concept for p in all_progress if p.mastery_score < 50.0]

    return MasteryOverviewResponse(
        overall_mastery=round(avg_mastery, 1),
        total_topics_studied=len(topics_set),
        total_concepts_learned=len(all_progress),
        strong_topics=strong[:10],
        weak_topics=weak[:10],
        concept_details=all_progress
    )


@router.get("/paths", response_model=List[LearningPathResponse])
def get_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    paths = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).all()
    if not paths:
        # Seed standard Learning Path
        default_nodes = [
            {"id": "node_1", "title": "Classical Mechanics: Newton's Laws", "difficulty": "beginner", "status": "completed", "progress": 100},
            {"id": "node_2", "title": "Work, Energy & Power", "difficulty": "intermediate", "status": "in_progress", "progress": 40},
            {"id": "node_3", "title": "Conservation of Momentum & Collisions", "difficulty": "intermediate", "status": "locked", "progress": 0},
            {"id": "node_4", "title": "Rotational Dynamics & Torque", "difficulty": "advanced", "status": "locked", "progress": 0},
            {"id": "node_5", "title": "Gravitation & Satellite Orbits", "difficulty": "advanced", "status": "locked", "progress": 0}
        ]
        sample_path = LearningPath(
            user_id=current_user.id,
            topic="Physics & Classical Mechanics Roadmap",
            description="From fundamental Newtonian kinematics to planetary astrophysics.",
            nodes=default_nodes,
            current_node_id="node_2",
            status="active",
            progress_percentage=28
        )
        db.add(sample_path)
        db.commit()
        db.refresh(sample_path)
        return [sample_path]
    return paths


@router.get("/{topic}", response_model=List[ConceptMasteryItem])
def get_topic_progress(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.topic.ilike(f"%{topic}%")
    ).all()
    return progress
