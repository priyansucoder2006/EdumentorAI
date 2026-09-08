import re
from typing import Dict, Any, List, Optional
from app.ai.providers import get_llm_provider
from app.models.lesson import Lesson, LessonStep
from app.core.logging import logger


class LanguageAdapterService:
    """
    Generic multilingual pedagogical translation & localization layer.
    Supports English, Hindi, Hinglish, and Bengali across arbitrary subjects.
    Crucially shields mathematical formulas ($F=ma$, $V=IR$), programming code,
    and technical identifiers while translating surrounding pedagogical explanations and questions.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def adapt_lesson_language(self, lesson: Lesson, target_language: str) -> Lesson:
        """
        Translates all lesson steps into the target language while preserving
        current step index, mastery progress, state, and canonical formulas.
        """
        target_lang = target_language.lower()
        if lesson.language and lesson.language.lower() == target_lang:
            return lesson

        lesson.language = target_lang

        for step in lesson.steps:
            # 1. Translate Explanation
            if step.explanation:
                step.explanation = await self.translate_text(
                    text=step.explanation,
                    target_language=target_lang,
                    context=f"Subject Concept: {step.concept}"
                )

            # 2. Translate Analogy
            if step.analogy:
                step.analogy = await self.translate_text(
                    text=step.analogy,
                    target_language=target_lang,
                    context=f"Analogy for: {step.concept}"
                )

            # 3. Translate Question & Options
            if step.question and isinstance(step.question, dict):
                q = dict(step.question)
                if q.get("prompt"):
                    q["prompt"] = await self.translate_text(
                        text=q["prompt"],
                        target_language=target_lang,
                        context=f"Question for: {step.concept}"
                    )
                if q.get("options") and isinstance(q["options"], list):
                    translated_opts = []
                    for opt in q["options"]:
                        tr_opt = await self.translate_text(
                            text=str(opt),
                            target_language=target_lang,
                            context="Multiple Choice Option"
                        )
                        translated_opts.append(tr_opt)
                    q["options"] = translated_opts
                    if q.get("correct_answer") and len(q["options"]) > 0:
                        q["correct_answer"] = q["options"][0]
                step.question = q

        return lesson

    async def translate_text(
        self,
        text: str,
        target_language: str,
        context: Optional[str] = None
    ) -> str:
        """
        Translates text to target language while strictly preserving formulas and code.
        """
        if not text or not text.strip():
            return ""

        target_lang = target_language.lower()
        if target_lang in ["en", "english"]:
            return text

        # 1. Extract and protect formulas ($...$), LaTeX expressions, and code snippets
        protected_map: Dict[str, str] = {}
        counter = 0

        # Protect math expressions: $...$
        def math_sub(match):
            nonlocal counter
            key = f"__MATH_EXPR_{counter}__"
            protected_map[key] = match.group(0)
            counter += 1
            return key

        # Protect code snippets: `...`
        def code_sub(match):
            nonlocal counter
            key = f"__CODE_SNIPPET_{counter}__"
            protected_map[key] = match.group(0)
            counter += 1
            return key

        shielded_text = re.sub(r'\$[^\$]+\$', math_sub, text)
        shielded_text = re.sub(r'`[^`]+`', code_sub, shielded_text)

        # 2. Build translation prompt for LLM
        prompt = f"""You are a master educational translator and multilingual science educator.
Translate the following educational explanation into {target_language.upper()}.

CRITICAL RULES:
1. Preserve all placeholders like __MATH_EXPR_0__, __CODE_SNIPPET_0__ EXACTLY as they appear without translating them.
2. Keep the pedagogical tone warm, engaging, and clear for a student.
3. For Hinglish, use natural Hindi written in Roman English alphabet commonly used in Indian online education (e.g., 'Newton ka first law kehta hai ki...').
4. For Hindi (hi), use standard Devanagari script.
5. For Bengali (bn), use standard Bengali script.

Context: {context or 'Educational lesson explanation'}
Input Text:
{shielded_text}

Output ONLY the translated text, nothing else."""

        try:
            translated = await self.llm.generate_text(
                prompt=prompt,
                system_prompt="You are a professional educational multilingual localization engine."
            )
            translated = translated.strip().strip('"')

            # 3. Restore protected formulas and code
            for placeholder, original in protected_map.items():
                translated = translated.replace(placeholder, original)

            return translated
        except Exception as e:
            logger.error(f"Multilingual translation error: {e}")
            return text
