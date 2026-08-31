from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.lesson import Lesson, LessonStep
from app.models.interaction import Interaction
from app.schemas.interaction import AnswerSubmitRequest, InteractionResponse
from app.ai.agents.evaluator_agent import EvaluatorAgent
from app.ai.agents.misconception_agent import MisconceptionAgent
from app.services.adaptation_engine import AdaptationEngine
from app.services.mastery_model import MasteryModelService
from app.core.mongodb import MongoSyncService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/answer", response_model=InteractionResponse)
async def submit_answer(
    req: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    step = db.query(LessonStep).filter(LessonStep.id == req.step_id).first()
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson step not found.")

    lesson = db.query(Lesson).filter(Lesson.id == step.lesson_id, Lesson.user_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")
    q_data = step.question or {}
    q_prompt = q_data.get("prompt", step.concept)
    expected_answer = step.expected_answer or q_data.get("correct_answer", "")

    # 1. Semantic Evaluation
    evaluator = EvaluatorAgent()
    eval_result = await evaluator.evaluate_student_answer(
        concept=step.concept,
        question_prompt=q_prompt,
        expected_answer=expected_answer,
        student_answer=req.student_answer,
        difficulty=step.difficulty
    )

    # 2. Misconception Diagnosis (if wrong or partial)
    misconception_agent = MisconceptionAgent()
    if not eval_result.is_correct or eval_result.score < 0.70:
        misc_result = await misconception_agent.diagnose_misconception(
            concept=step.concept,
            question_prompt=q_prompt,
            expected_answer=expected_answer,
            student_answer=req.student_answer
        )
    else:
        misc_result = await misconception_agent.diagnose_misconception(
            concept=step.concept,
            question_prompt=q_prompt,
            expected_answer=expected_answer,
            student_answer="correct"
        )
        misc_result.detected = False
        misc_result.severity = "none"

    # 3. Deterministic Adaptation Decision
    adaptation_engine = AdaptationEngine()
    past_attempts = db.query(Interaction).filter(Interaction.step_id == step.id).count() + 1
    decision = adaptation_engine.decide_next_action(
        evaluation=eval_result,
        misconception=misc_result,
        current_step_concept=step.concept,
        current_step_data={
            "explanation": step.explanation,
            "example": step.example,
            "analogy": step.analogy
        },
        attempts_on_step=past_attempts
    )

    # 4. Multi-Factor Concept Mastery Calculation & Persistence
    mastery_service = MasteryModelService(db)
    progress_rec = mastery_service.update_concept_mastery(
        user_id=current_user.id,
        topic=lesson.topic,
        concept=step.concept,
        is_correct=eval_result.is_correct,
        score=eval_result.score,
        difficulty=step.difficulty,
        reasoning_quality=eval_result.reasoning_quality
    )

    # 5. Persist Interaction record
    interaction = Interaction(
        lesson_id=lesson.id,
        step_id=step.id,
        user_id=current_user.id,
        question=q_prompt,
        student_answer=req.student_answer,
        evaluation=eval_result.model_dump(),
        misconception=misc_result.model_dump(),
        adaptive_decision=decision.action,
        confidence=eval_result.confidence
    )
    db.add(interaction)

    # If reteach was decided, set step state to 'reteach'
    if decision.action == "reteach":
        step.state = "reteach"

    db.commit()
    db.refresh(interaction)

    # Sync interaction to MongoDB Atlas
    MongoSyncService.sync_interaction(current_user.id, lesson.id, {
        "step_id": step.id,
        "question": q_prompt,
        "student_answer": req.student_answer,
        "score": eval_result.score,
        "is_correct": eval_result.is_correct,
        "adaptive_decision": decision.action
    })

    return InteractionResponse(
        id=interaction.id,
        lesson_id=lesson.id,
        step_id=step.id,
        question=interaction.question,
        student_answer=interaction.student_answer,
        evaluation=eval_result,
        misconception=misc_result,
        adaptive_decision=decision,
        confidence=interaction.confidence,
        current_mastery=progress_rec.mastery_score,
        created_at=interaction.created_at
    )


@router.get("/{lesson_id}", response_model=List[InteractionResponse])
def get_lesson_interactions(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.user_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")

    interactions = (
        db.query(Interaction)
        .filter(Interaction.lesson_id == lesson_id, Interaction.user_id == current_user.id)
        .order_by(Interaction.created_at.asc())
        .all()
    )
    res = []
    for it in interactions:
        res.append(
            InteractionResponse(
                id=it.id,
                lesson_id=it.lesson_id,
                step_id=it.step_id,
                question=it.question,
                student_answer=it.student_answer,
                evaluation=it.evaluation or {},
                misconception=it.misconception or {},
                adaptive_decision={
                    "action": it.adaptive_decision,
                    "rationale": "Historical interaction record",
                    "new_mastery_estimate": 70.0
                },
                confidence=it.confidence,
                current_mastery=75.0,
                created_at=it.created_at
            )
        )
    return res
