from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.learning_progress import LearningProgress
from app.models.learner_profile import LearnerProfile
from app.core.logging import logger


class MasteryModelService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_interaction_mastery(
        self,
        correctness_score: float,  # 0.0 to 1.0
        attempts: int,
        correct_attempts: int,
        difficulty: str = "beginner",
        reasoning_quality: str = "good",
        days_since_last_studied: float = 0.0
    ) -> float:
        """
        Computes normalized mastery score (0 to 100) using the multi-factor transparent formula:
        mastery = 100 * (0.35 * correctness + 0.25 * consistency + 0.20 * difficulty_factor + 0.10 * reasoning + 0.10 * retention)
        """
        # 1. Correctness (0.0 to 1.0)
        c = max(0.0, min(1.0, correctness_score))

        # 2. Consistency: correct / attempts ratio
        consistency = (correct_attempts / attempts) if attempts > 0 else c

        # 3. Difficulty multiplier
        diff_weights = {"beginner": 0.60, "intermediate": 0.85, "advanced": 1.00}
        d_factor = diff_weights.get(difficulty.lower(), 0.70)

        # 4. Reasoning quality
        reasoning_weights = {"poor": 0.25, "partial": 0.55, "good": 0.85, "excellent": 1.00}
        r_factor = reasoning_weights.get(reasoning_quality.lower(), 0.75)

        # 5. Retention factor (Ebbinghaus forgetting curve simulation)
        retention = max(0.5, 1.0 - (days_since_last_studied * 0.03))

        raw_score = (
            0.35 * c +
            0.25 * consistency +
            0.20 * d_factor +
            0.10 * r_factor +
            0.10 * retention
        )

        normalized_mastery = round(max(0.0, min(100.0, raw_score * 100.0)), 1)
        return normalized_mastery

    def update_concept_mastery(
        self,
        user_id: str,
        topic: str,
        concept: str,
        is_correct: bool,
        score: float,
        difficulty: str = "beginner",
        reasoning_quality: str = "good"
    ) -> LearningProgress:
        """
        Persists progress for a concept and updates the user's aggregate learner profile.
        """
        progress_record = (
            self.db.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.topic == topic,
                LearningProgress.concept == concept
            )
            .first()
        )

        now = datetime.now(timezone.utc)

        if not progress_record:
            progress_record = LearningProgress(
                user_id=user_id,
                topic=topic,
                concept=concept,
                mastery_score=0.0,
                attempts=1,
                correct_attempts=1 if is_correct else 0,
                difficulty_level=difficulty,
                last_studied=now
            )
            self.db.add(progress_record)
        else:
            progress_record.attempts += 1
            if is_correct:
                progress_record.correct_attempts += 1
            progress_record.last_studied = now
            progress_record.difficulty_level = difficulty

        # Calculate new mastery score
        new_mastery = self.calculate_interaction_mastery(
            correctness_score=score,
            attempts=progress_record.attempts,
            correct_attempts=progress_record.correct_attempts,
            difficulty=difficulty,
            reasoning_quality=reasoning_quality
        )
        progress_record.mastery_score = new_mastery
        self.db.commit()
        self.db.refresh(progress_record)

        # Update LearnerProfile strong/weak topics
        self._sync_learner_profile_topics(user_id)

        return progress_record

    def _sync_learner_profile_topics(self, user_id: str):
        profile = self.db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
        if not profile:
            return

        all_progress = self.db.query(LearningProgress).filter(LearningProgress.user_id == user_id).all()
        strong = []
        weak = []

        for p in all_progress:
            if p.mastery_score >= 75.0:
                if p.concept not in strong:
                    strong.append(p.concept)
            elif p.mastery_score < 50.0:
                if p.concept not in weak:
                    weak.append(p.concept)

        profile.strong_topics = strong[:10]
        profile.weak_topics = weak[:10]
        self.db.commit()
