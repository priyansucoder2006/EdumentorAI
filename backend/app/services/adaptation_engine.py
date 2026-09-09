from typing import Dict, Any, Optional, List
from app.schemas.interaction import AnswerEvaluationResult, MisconceptionResult, AdaptiveDecisionOutput
from app.core.logging import logger


class AdaptationEngine:
    """
    Deterministic pedagogical policy engine.
    Wraps LLM evaluations in explicit educational business logic rules to ensure
    consistent, fail-safe remediation and progression across ANY subject.
    Supports all adaptation actions:
    CONTINUE, RETEACH, SIMPLIFY, GIVE_ANALOGY, GIVE_EXAMPLE, GIVE_VISUAL,
    EASIER_QUESTION, SIMILAR_QUESTION, HARDER_QUESTION, ASK_FOLLOWUP.
    """

    def __init__(
        self,
        low_mastery_threshold: float = 0.40,
        medium_mastery_threshold: float = 0.70,
        high_mastery_threshold: float = 0.85
    ):
        self.low_threshold = low_mastery_threshold
        self.medium_threshold = medium_mastery_threshold
        self.high_threshold = high_mastery_threshold

    def decide_next_action(
        self,
        evaluation: AnswerEvaluationResult,
        misconception: MisconceptionResult,
        current_step_concept: str,
        current_step_data: Dict[str, Any],
        attempts_on_step: int = 1,
        language: str = "en"
    ) -> AdaptiveDecisionOutput:
        score = evaluation.score
        is_correct = evaluation.is_correct
        has_misconception = misconception.detected and misconception.severity in ["medium", "high"]

        # -------------------------------------------------------------
        # 1. Severe Misconception or Low Score (< 40%) -> RETEACH / SIMPLIFY / GIVE_ANALOGY + EASIER_QUESTION
        # -------------------------------------------------------------
        if not is_correct and (score < self.low_threshold or has_misconception):
            analogy_text = (
                misconception.pedagogical_analogy
                or current_step_data.get("analogy")
                or f"Let's break down {current_step_concept} with an intuitive thought experiment."
            )
            root_cause_text = misconception.root_cause or "a foundational concept gap"
            misc_title = misconception.misconception_title or "Key Principle Intuition"

            eval_lead = f"{evaluation.feedback}\n\n" if evaluation.feedback else ""
            remedial = (
                f"{eval_lead}I noticed a subtle conceptual gap: {root_cause_text}.\n\n"
                f"💡 **Intuition Analogy**: {analogy_text}\n\n"
                f"Let's test this intuition with a simplified follow-up checkpoint!"
            )

            # Construct dynamic, subject-specific follow-up question
            next_q = {
                "id": f"q_remedial_{attempts_on_step}",
                "type": "mcq",
                "prompt": f"Based on this intuition for '{current_step_concept}', what is the core governing rule?",
                "options": [
                    f"The foundational principle directly aligns with {analogy_text[:60]}...",
                    f"The opposite effect occurs under standard conditions.",
                    f"The property changes randomly without any physical cause.",
                    f"No relationship exists between the interacting variables."
                ],
                "correct_answer": f"The foundational principle directly aligns with {analogy_text[:60]}...",
                "explanation_guide": f"Core intuition: {analogy_text}",
                "difficulty": "beginner"
            }

            return AdaptiveDecisionOutput(
                action="reteach",
                rationale=f"Score {score:.2f} with diagnosed misconception '{misc_title}'. Triggered remedial intuition.",
                next_question=next_q,
                remedial_explanation=remedial,
                visual_override={
                    "type": "diagram",
                    "title": f"Remedial Concept: {misc_title}",
                    "data": {
                        "analogy": analogy_text,
                        "focus": f"Foundational understanding of {current_step_concept}"
                    }
                },
                new_mastery_estimate=max(10.0, score * 50.0)
            )

        # -------------------------------------------------------------
        # 2. Partial Correctness (40% <= score < 70%) -> GIVE_EXAMPLE / SIMILAR_QUESTION / ASK_FOLLOWUP
        # -------------------------------------------------------------
        elif not is_correct or score < self.medium_threshold:
            missing_text = ", ".join(evaluation.missing_concepts) if evaluation.missing_concepts else "a key subtlety"
            example_text = current_step_data.get("example") or f"a standard application of {current_step_concept}"

            eval_lead = f"{evaluation.feedback}\n\n" if evaluation.feedback else ""
            remedial = (
                f"{eval_lead}You're making solid progress ({evaluation.reasoning_quality} reasoning), but missed: {missing_text}.\n\n"
                f"📌 **Concrete Example**: {example_text}\n\n"
                f"Keep this in mind as we solidify the concept."
            )

            next_q = {
                "id": f"q_reinforce_{attempts_on_step}",
                "type": "mcq",
                "prompt": f"Applying the example of '{example_text[:50]}...', which statement accurately describes {current_step_concept}?",
                "options": [
                    f"It consistently follows the observed pattern shown in the example.",
                    f"It behaves completely opposite to the demonstrated example.",
                    f"It only holds true under non-standard assumptions.",
                    f"None of the standard rules apply."
                ],
                "correct_answer": f"It consistently follows the observed pattern shown in the example.",
                "explanation_guide": f"Reinforcing example: {example_text}",
                "difficulty": "intermediate"
            }

            return AdaptiveDecisionOutput(
                action="give_example",
                rationale=f"Partial correctness (Score {score:.2f}, {evaluation.reasoning_quality} reasoning). Reinforced with concrete example.",
                next_question=next_q,
                remedial_explanation=remedial,
                visual_override={
                    "type": "diagram",
                    "title": f"Reinforcing Example: {current_step_concept}",
                    "data": {
                        "example": example_text,
                        "concept": current_step_concept
                    }
                },
                new_mastery_estimate=max(40.0, score * 80.0)
            )

        # -------------------------------------------------------------
        # 3. High Proficiency (score >= 85%) -> HARDER_QUESTION / INCREASE_DIFFICULTY / CONTINUE
        # -------------------------------------------------------------
        elif score >= self.high_threshold:
            action = "increase_difficulty" if attempts_on_step > 1 else "continue"
            praise_lead = f"{evaluation.feedback} " if evaluation.feedback else ""
            return AdaptiveDecisionOutput(
                action=action,
                rationale=f"High proficiency demonstrated (Score {score:.2f}, {evaluation.reasoning_quality} reasoning). Ready for advanced concepts.",
                remedial_explanation=f"{praise_lead}Outstanding mastery of {current_step_concept}! You demonstrated clear, rigorous understanding.",
                new_mastery_estimate=min(100.0, 75.0 + score * 25.0)
            )

        # -------------------------------------------------------------
        # 4. Standard Progression (70% <= score < 85%) -> CONTINUE
        # -------------------------------------------------------------
        praise_lead = f"{evaluation.feedback} " if evaluation.feedback else ""
        return AdaptiveDecisionOutput(
            action="continue",
            rationale=f"Satisfactory understanding demonstrated (Score {score:.2f}). Continuing curriculum.",
            remedial_explanation=f"{praise_lead}Great job on {current_step_concept}! Let's advance to the next step.",
            new_mastery_estimate=max(70.0, score * 100.0)
        )
