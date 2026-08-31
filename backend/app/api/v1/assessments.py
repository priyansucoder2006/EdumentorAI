from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.lesson import Lesson
from app.models.assessment import Assessment
from app.schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentSubmitRequest,
    AssessmentResponse,
    AssessmentLLMOutput
)
from app.ai.providers import get_llm_provider
from app.ai.prompts.visual import ASSESSMENT_SYSTEM_PROMPT
from app.ai.agents.recommender_agent import RecommenderAgent
from app.services.mastery_model import MasteryModelService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/generate", response_model=AssessmentResponse)
async def generate_assessment(
    req: AssessmentGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == req.lesson_id, Lesson.user_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")

    llm = get_llm_provider()
    concepts_list = [s.concept for s in lesson.steps]
    
    prompt = f"""Generate a 3-question comprehensive assessment for lesson on '{lesson.topic}'.
Concepts taught:
{', '.join(concepts_list)}
Difficulty: {lesson.difficulty}
Language: {lesson.language}"""

    generated_output: AssessmentLLMOutput = await llm.generate_structured(
        prompt=prompt,
        response_schema=AssessmentLLMOutput,
        system_prompt=ASSESSMENT_SYSTEM_PROMPT
    )

    questions_payload = [q.model_dump() for q in generated_output.questions]

    assessment = Assessment(
        lesson_id=lesson.id,
        user_id=current_user.id,
        score=0.0,
        total_questions=len(questions_payload),
        correct_count=0,
        questions_data=questions_payload,
        student_responses=[],
        strong_concepts=[],
        weak_concepts=[],
        recommendations=[]
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.post("/{assessment_id}/submit", response_model=AssessmentResponse)
def submit_assessment(
    assessment_id: str,
    req: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    lesson = db.query(Lesson).filter(Lesson.id == assessment.lesson_id, Lesson.user_id == current_user.id).first()
    questions = assessment.questions_data or []
    student_ans_map = {a.question_id: a.answer for a in req.answers}

    correct_count = 0
    strong = []
    weak = []
    responses_record = []

    for q in questions:
        q_id = q.get("id")
        user_ans = student_ans_map.get(q_id, "")
        correct_ans = q.get("correct_answer", "")
        concept = q.get("concept", "General")

        is_match = (user_ans.strip().lower() == correct_ans.strip().lower()) or (correct_ans.strip().lower() in user_ans.strip().lower())

        if is_match:
            correct_count += 1
            if concept not in strong:
                strong.append(concept)
        else:
            if concept not in weak:
                weak.append(concept)

        responses_record.append({
            "question_id": q_id,
            "prompt": q.get("prompt"),
            "student_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_match,
            "explanation": q.get("explanation")
        })

    total_q = len(questions) or 1
    final_score = round((correct_count / total_q) * 100.0, 1)

    # Recommender Engine
    recommender = RecommenderAgent()
    recs = recommender.generate_recommendations(
        topic=lesson.topic if lesson else "General Subject",
        overall_mastery=final_score,
        weak_concepts=weak,
        strong_concepts=strong,
        misconceptions=[]
    )

    assessment.score = final_score
    assessment.correct_count = correct_count
    assessment.strong_concepts = strong
    assessment.weak_concepts = weak
    assessment.student_responses = responses_record
    assessment.recommendations = [r.model_dump() for r in recs]

    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return assessment
