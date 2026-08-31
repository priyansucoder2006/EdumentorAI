from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.lesson import Lesson
from app.schemas.lesson import (
    LessonCreate,
    LessonResponse,
    LessonLanguageSwitch,
    LessonStateTransitionRequest
)
from app.services.teaching_state_machine import TeachingStateMachine
from app.api.deps import get_current_user

router = APIRouter()


@router.post("", response_model=LessonResponse)
async def create_lesson(
    lesson_in: LessonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    state_machine = TeachingStateMachine(db)
    lesson = await state_machine.create_and_initialize_lesson(
        user_id=current_user.id,
        lesson_in=lesson_in
    )
    return lesson


@router.get("", response_model=List[LessonResponse])
def get_lessons(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lessons = db.query(Lesson).filter(Lesson.user_id == current_user.id).order_by(Lesson.created_at.desc()).all()
    return lessons


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.user_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")
    return lesson


@router.post("/{lesson_id}/state", response_model=LessonResponse)
def transition_lesson_state(
    lesson_id: str,
    req: LessonStateTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.user_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")

    state_machine = TeachingStateMachine(db)
    if req.action == "next_step":
        return state_machine.advance_to_next_step(lesson_id)
    elif req.action == "switch_language" and req.target_language:
        return state_machine.switch_language_in_lesson(lesson_id, req.target_language)
    return state_machine.transition_state(lesson_id, req.action.upper())


@router.post("/{lesson_id}/language", response_model=LessonResponse)
def switch_lesson_language(
    lesson_id: str,
    req: LessonLanguageSwitch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.user_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")

    state_machine = TeachingStateMachine(db)
    return state_machine.switch_language_in_lesson(lesson_id, req.target_language)
