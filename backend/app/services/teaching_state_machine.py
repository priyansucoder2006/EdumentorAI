from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.lesson import Lesson, LessonStep
from app.models.interaction import Interaction
from app.models.learner_profile import LearnerProfile
from app.schemas.lesson import LessonCreate, LessonPlanLLMOutput
from app.ai.agents.planner_agent import LessonPlannerAgent
from app.core.logging import logger


class TeachingStateMachine:
    """
    Pedagogical State Machine orchestrating the 10-step adaptive teaching loop:
    UNDERSTAND -> PLAN -> EXPLAIN -> DEMONSTRATE -> QUESTION -> EVALUATE -> ADAPT -> CONTINUE -> ASSESS -> REMEMBER
    """

    def __init__(self, db: Session):
        self.db = db
        self.planner_agent = LessonPlannerAgent(db)

    async def create_and_initialize_lesson(
        self,
        user_id: str,
        lesson_in: LessonCreate
    ) -> Lesson:
        # 1. Fetch learner profile
        profile = self.db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
        profile_dict = {
            "knowledge_level": profile.knowledge_level if profile else "beginner",
            "learning_style": profile.learning_style if profile else "visual"
        }

        # 2. Plan lesson via AI Planner Agent
        plan: LessonPlanLLMOutput = await self.planner_agent.plan_lesson(lesson_in, profile_dict)

        # 3. Create Lesson Database Record
        db_lesson = Lesson(
            user_id=user_id,
            topic=plan.topic,
            document_id=lesson_in.document_id,
            language=lesson_in.language,
            difficulty=lesson_in.difficulty,
            duration_minutes=lesson_in.duration_minutes,
            objectives=plan.objectives,
            status="in_progress",
            current_step_index=0,
            state="EXPLAIN",
            lesson_metadata={
                "summary": plan.summary,
                "prerequisites": plan.prerequisites,
                "target_audience": lesson_in.target_audience
            }
        )
        self.db.add(db_lesson)
        self.db.flush()

        # 4. Create LessonStep Database Records
        for s in plan.steps:
            db_step = LessonStep(
                lesson_id=db_lesson.id,
                step_number=s.step_number,
                concept=s.concept,
                explanation=s.explanation,
                example=s.example,
                analogy=s.analogy,
                visual_type=s.visual_type,
                visual_data=s.visual_data,
                question=s.question.model_dump(),
                expected_answer=s.expected_answer,
                difficulty=s.difficulty,
                state="active" if s.step_number == 1 else "pending"
            )
            self.db.add(db_step)

        self.db.commit()
        self.db.refresh(db_lesson)
        return db_lesson

    def transition_state(self, lesson_id: str, new_state: str) -> Lesson:
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found.")
        lesson.state = new_state
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def advance_to_next_step(self, lesson_id: str) -> Lesson:
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found.")

        steps = sorted(lesson.steps, key=lambda s: s.step_number)
        current_idx = lesson.current_step_index

        # Mark current step completed
        if current_idx < len(steps):
            steps[current_idx].state = "completed"

        # Advance or Complete
        if current_idx + 1 < len(steps):
            lesson.current_step_index += 1
            steps[current_idx + 1].state = "active"
            lesson.state = "EXPLAIN"
        else:
            lesson.status = "completed"
            lesson.state = "ASSESS"

        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def switch_language_in_lesson(self, lesson_id: str, target_language: str) -> Lesson:
        """
        Updates the lesson teaching language while preserving current step index,
        mastery progress, and canonical formula structures.
        """
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found.")

        lesson.language = target_language

        # Hinglish translations for standard concepts
        if target_language.lower() in ["hinglish", "hi"]:
            for step in lesson.steps:
                if "Inertia" in step.concept:
                    step.explanation = "Newton ka First Law (Law of Inertia) kehta hai ki koi object tab tak apni state change nahi karega jab tak uspar koi bahari force na lage."
                    step.analogy = "Socho ek frictionless ice surface par hockey puck ko slide kiya—wo bina ruke chalti rahegi!"
                elif "Second Law" in step.concept:
                    step.explanation = "Newton ka Second Law ($F = ma$) batata hai ki Force aur Acceleration directly proportional hote hain."
                    step.analogy = "Bicycle ko push karna easy hai, lekin heavy truck ko push karne ke liye bohot zyada force chahiye."

        self.db.commit()
        self.db.refresh(lesson)
        return lesson
