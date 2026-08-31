from typing import Optional, Dict, Any
from app.ai.providers import get_llm_provider
from app.ai.prompts.evaluator import EVALUATOR_SYSTEM_PROMPT, EVALUATOR_PROMPT_TEMPLATE
from app.schemas.interaction import AnswerEvaluationResult
from app.core.logging import logger


class EvaluatorAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    async def evaluate_student_answer(
        self,
        concept: str,
        question_prompt: str,
        expected_answer: str,
        student_answer: str,
        difficulty: str = "beginner"
    ) -> AnswerEvaluationResult:
        """
        Evaluates student answer semantically without rigid keyword dependence.
        """
        prompt = EVALUATOR_PROMPT_TEMPLATE.format(
            concept=concept,
            question_prompt=question_prompt,
            expected_answer=expected_answer,
            student_answer=student_answer,
            difficulty=difficulty
        )

        result = await self.llm.generate_structured(
            prompt=prompt,
            response_schema=AnswerEvaluationResult,
            system_prompt=EVALUATOR_SYSTEM_PROMPT
        )
        return result
