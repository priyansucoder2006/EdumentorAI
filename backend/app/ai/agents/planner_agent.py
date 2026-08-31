from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.ai.providers import get_llm_provider
from app.ai.prompts.planner import PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT_TEMPLATE
from app.schemas.lesson import LessonPlanLLMOutput, LessonCreate
from app.services.vector_store import VectorStoreService
from app.core.logging import logger


class LessonPlannerAgent:
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStoreService(db)
        self.llm = get_llm_provider()

    async def plan_lesson(
        self,
        lesson_in: LessonCreate,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> LessonPlanLLMOutput:
        """
        Creates a time-aware, level-appropriate, RAG-grounded structured lesson plan.
        """
        rag_context = "No specific uploaded document referenced. Use general domain knowledge."
        if lesson_in.document_id:
            chunks = await self.vector_store.search_similar_chunks(
                query=lesson_in.topic,
                document_id=lesson_in.document_id,
                top_k=5
            )
            if chunks:
                rag_context = "\n".join([f"- [Page {c['page_number']}] {c['chunk_text']}" for c in chunks])

        target_audience = lesson_in.target_audience or "General Learner"
        if user_profile and user_profile.get("knowledge_level"):
            target_audience = f"{user_profile.get('knowledge_level')} learner ({target_audience})"

        prompt = PLANNER_USER_PROMPT_TEMPLATE.format(
            topic=lesson_in.topic,
            duration_minutes=lesson_in.duration_minutes,
            difficulty=lesson_in.difficulty,
            target_audience=target_audience,
            language=lesson_in.language,
            learning_goal=lesson_in.learning_goal or "mastery",
            rag_context=rag_context
        )

        plan = await self.llm.generate_structured(
            prompt=prompt,
            response_schema=LessonPlanLLMOutput,
            system_prompt=PLANNER_SYSTEM_PROMPT
        )
        return plan
