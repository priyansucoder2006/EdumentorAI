import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.models.lesson import Lesson, LessonStep
from app.core.config import settings
from app.core.logging import logger


class VideoScene(BaseModel):
    scene_id: str
    scene_number: int
    scene_type: str  # intro, concept_explanation, demonstration, visual_focus, formative_check, summary
    title: str
    concept: str
    narration: str
    on_screen_text: str
    visual_type: str  # text_card, math, code, diagram, graph, simulation
    visual_data: Dict[str, Any] = {}
    avatar_mood: str = "explaining"  # explaining, questioning, praising, remedial
    estimated_duration_seconds: float = 6.0


class ScenePlanner:
    """
    Transforms any structured Lesson into a streamlined, high-impact video storyboard.
    Curates the most essential pedagogical scenes (3-5 milestone scenes) for rapid generation.
    """

    @staticmethod
    def plan_scenes_for_lesson(lesson: Lesson, max_scenes: int = None) -> List[VideoScene]:
        if max_scenes is None:
            max_scenes = settings.VIDEO_MAX_SCENES or 5

        scenes: List[VideoScene] = []
        scene_idx = 1
        sorted_steps = sorted(lesson.steps, key=lambda s: s.step_number) if lesson.steps else []

        # 1. INTRO SCENE
        intro_narration = (
            f"Welcome to our AI masterclass on {lesson.topic}. "
            f"Today, we will build a deep, intuitive understanding step by step. Let's begin!"
        )
        scenes.append(VideoScene(
            scene_id=f"scene_{scene_idx}",
            scene_number=scene_idx,
            scene_type="intro",
            title=lesson.topic,
            concept="Introduction & Overview",
            narration=intro_narration,
            on_screen_text=f"{lesson.topic}\n\nKey Objectives:\n" + "\n".join([f"• {obj}" for obj in (lesson.objectives or [])[:3]]),
            visual_type="text_card",
            visual_data={
                "badge": "Masterclass Overview",
                "title": lesson.topic,
                "items": lesson.objectives or ["Master core foundational principles", "Apply concepts to real-world problems"]
            },
            avatar_mood="explaining",
            estimated_duration_seconds=max(4.0, len(intro_narration.split()) * 0.35)
        ))
        scene_idx += 1

        # 2. SELECT TOP 1-2 CORE CONCEPT SCENES
        primary_step = sorted_steps[0] if sorted_steps else None
        if primary_step:
            clean_exp = re.sub(r'[\*\#\`\_]', '', primary_step.explanation or '')
            exp_narration = f"First, let's understand {primary_step.concept}. {clean_exp[:140]}"
            scenes.append(VideoScene(
                scene_id=f"scene_{scene_idx}",
                scene_number=scene_idx,
                scene_type="concept_explanation",
                title=f"Core Principle: {primary_step.concept}",
                concept=primary_step.concept,
                narration=exp_narration,
                on_screen_text=f"{primary_step.concept}\n\n{clean_exp[:180]}",
                visual_type=primary_step.visual_type or "text_card",
                visual_data=primary_step.visual_data or {
                    "title": primary_step.concept,
                    "explanation": clean_exp,
                    "example": primary_step.example
                },
                avatar_mood="explaining",
                estimated_duration_seconds=max(5.0, len(exp_narration.split()) * 0.35)
            ))
            scene_idx += 1

        # 3. INTUITION / ANALOGY / DEMONSTRATION SCENE
        analogy_step = next((s for s in sorted_steps if s.analogy), primary_step)
        if analogy_step and analogy_step.analogy:
            clean_analogy = re.sub(r'[\*\#\`\_]', '', analogy_step.analogy)
            demo_narration = f"To make this intuitive, think of it like this: {clean_analogy}"
            scenes.append(VideoScene(
                scene_id=f"scene_{scene_idx}",
                scene_number=scene_idx,
                scene_type="demonstration",
                title=f"Intuition: {analogy_step.concept}",
                concept=analogy_step.concept,
                narration=demo_narration,
                on_screen_text=f"💡 Intuition & Analogy\n\n{clean_analogy}",
                visual_type="diagram",
                visual_data={
                    "title": f"Intuition for {analogy_step.concept}",
                    "analogy": clean_analogy,
                    "example": analogy_step.example
                },
                avatar_mood="explaining",
                estimated_duration_seconds=max(5.0, len(demo_narration.split()) * 0.35)
            ))
            scene_idx += 1

        # 4. FORMATIVE CHECKPOINT SCENE
        question_step = next((s for s in sorted_steps if s.question), None)
        if question_step and len(scenes) < max_scenes - 1:
            q_data = question_step.question
            if isinstance(q_data, dict):
                q_prompt = q_data.get("prompt") or str(q_data)
                q_options = q_data.get("options", [])
                q_ans = question_step.expected_answer or q_data.get("correct_answer", "")
            else:
                q_prompt = str(q_data)
                q_options = []
                q_ans = question_step.expected_answer or ""

            check_narration = f"Now, a quick check: {q_prompt}"
            scenes.append(VideoScene(
                scene_id=f"scene_{scene_idx}",
                scene_number=scene_idx,
                scene_type="formative_check",
                title=f"Checkpoint: {question_step.concept}",
                concept=question_step.concept,
                narration=check_narration,
                on_screen_text=f"❓ Checkpoint Question\n\n{q_prompt}\n\nCore Answer: {q_ans[:80]}",
                visual_type="text_card",
                visual_data={
                    "badge": "Checkpoint Question",
                    "prompt": q_prompt,
                    "options": q_options,
                    "correct_answer": q_ans
                },
                avatar_mood="questioning",
                estimated_duration_seconds=max(4.5, len(check_narration.split()) * 0.35)
            ))
            scene_idx += 1

        # 5. SUMMARY & NEXT STEPS SCENE
        summary_narration = (
            f"Great job! You now understand the core foundations of {lesson.topic}. "
            f"Proceed to the interactive quiz to test your mastery."
        )
        scenes.append(VideoScene(
            scene_id=f"scene_{scene_idx}",
            scene_number=scene_idx,
            scene_type="summary",
            title="Lesson Mastery & Summary",
            concept=lesson.topic,
            narration=summary_narration,
            on_screen_text=f"🎉 Mastery Achieved: {lesson.topic}\n\n• Foundational intuition grasped\n• Ready for adaptive assessment",
            visual_type="text_card",
            visual_data={
                "badge": "Mastery Achieved",
                "title": f"Mastered: {lesson.topic}",
                "items": [s.concept for s in sorted_steps[:4]] if sorted_steps else ["Core Foundations"]
            },
            avatar_mood="praising",
            estimated_duration_seconds=max(4.0, len(summary_narration.split()) * 0.35)
        ))

        return scenes[:max_scenes]
