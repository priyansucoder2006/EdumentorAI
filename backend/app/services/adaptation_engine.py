from typing import Dict, Any, Optional
from app.schemas.interaction import AnswerEvaluationResult, MisconceptionResult, AdaptiveDecisionOutput
from app.core.logging import logger


class AdaptationEngine:
    """
    Deterministic pedagogical policy engine.
    Wraps LLM evaluations in explicit educational business logic rules to ensure
    consistent, fail-safe remediation and progression.
    """

    def decide_next_action(
        self,
        evaluation: AnswerEvaluationResult,
        misconception: MisconceptionResult,
        current_step_concept: str,
        current_step_data: Dict[str, Any],
        attempts_on_step: int = 1
    ) -> AdaptiveDecisionOutput:
        score = evaluation.score
        is_correct = evaluation.is_correct
        has_misconception = misconception.detected and misconception.severity in ["medium", "high"]

        # Policy Rule 1: Severe Misconception or Low Score (< 0.40) -> Reteach with Analogy + Easier Question
        if not is_correct and (score < 0.40 or has_misconception):
            analogy_text = misconception.pedagogical_analogy or current_step_data.get("analogy") or "Let's simplify this concept with an intuitive thought experiment."
            remedial = (
                f"I noticed a conceptual gap: {misconception.root_cause or 'Let us look at this differently'}.\n\n"
                f"💡 **Analogy**: {analogy_text}\n\n"
                f"Let's test this intuition with a clearer follow-up check!"
            )
            
            # Construct simpler follow-up question
            next_q = {
                "id": f"q_remedial_{attempts_on_step}",
                "type": "mcq",
                "prompt": f"Based on this analogy, if no force opposes motion on frictionless ice, what happens to speed?",
                "options": [
                    "Speed stays constant indefinitely without any pushing force.",
                    "Speed decreases quickly.",
                    "The object accelerates to the speed of light.",
                    "The object vanishes."
                ],
                "correct_answer": "Speed stays constant indefinitely without any pushing force.",
                "explanation_guide": "Without friction or drag, velocity remains constant (Law of Inertia).",
                "difficulty": "beginner"
            }

            return AdaptiveDecisionOutput(
                action="reteach",
                rationale=f"Score {score:.2f} with detected misconception '{misconception.misconception_title or 'concept error'}'. Triggered remedial analogy.",
                next_question=next_q,
                remedial_explanation=remedial,
                visual_override={
                    "type": "diagram",
                    "title": f"Remedial Concept: {misconception.misconception_title or 'Intuition Visual'}",
                    "data": {"analogy": analogy_text, "focus": "No net external force = Constant velocity"}
                },
                new_mastery_estimate=max(10.0, score * 50.0)
            )

        # Policy Rule 2: Partial Correctness (0.40 <= score < 0.70) -> Provide Concrete Example & Similar Check
        elif not is_correct or score < 0.70:
            remedial = (
                f"You're on the right track ({evaluation.reasoning_quality} reasoning), but missed: {', '.join(evaluation.missing_concepts) if evaluation.missing_concepts else 'a subtle nuance'}.\n\n"
                f"📌 **Key Takeaway**: Remember that forces always act in equal and opposite pairs on separate objects."
            )
            return AdaptiveDecisionOutput(
                action="provide_analogy",
                rationale=f"Partial correctness (Score {score:.2f}). Provided reinforcing tip.",
                remedial_explanation=remedial,
                new_mastery_estimate=score * 80.0
            )

        # Policy Rule 3: High Mastery (score >= 0.85) -> Advance or Increase Difficulty
        elif score >= 0.85:
            return AdaptiveDecisionOutput(
                action="continue" if attempts_on_step <= 1 else "increase_difficulty",
                rationale=f"High proficiency demonstrated (Score {score:.2f}, {evaluation.reasoning_quality} reasoning). Ready for next concept.",
                new_mastery_estimate=min(100.0, 75.0 + score * 25.0)
            )

        # Policy Rule 4: Standard Progression
        return AdaptiveDecisionOutput(
            action="continue",
            rationale="Satisfactory understanding demonstrated.",
            new_mastery_estimate=70.0
        )
