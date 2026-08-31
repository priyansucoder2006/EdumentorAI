from typing import Optional, Dict, Any
from app.ai.providers import get_llm_provider
from app.ai.prompts.misconception import MISCONCEPTION_SYSTEM_PROMPT, MISCONCEPTION_PROMPT_TEMPLATE
from app.schemas.interaction import MisconceptionResult
from app.core.logging import logger


class MisconceptionAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    async def diagnose_misconception(
        self,
        concept: str,
        question_prompt: str,
        expected_answer: str,
        student_answer: str
    ) -> MisconceptionResult:
        """
        Diagnoses why the student made an error and identifies root cause mental models.
        """
        prompt = MISCONCEPTION_PROMPT_TEMPLATE.format(
            concept=concept,
            question_prompt=question_prompt,
            expected_answer=expected_answer,
            student_answer=student_answer
        )

        result = await self.llm.generate_structured(
            prompt=prompt,
            response_schema=MisconceptionResult,
            system_prompt=MISCONCEPTION_SYSTEM_PROMPT
        )
        return result
