import pytest
from app.ai.agents.evaluator_agent import EvaluatorAgent
from app.ai.agents.misconception_agent import MisconceptionAgent
from app.services.adaptation_engine import AdaptationEngine
from app.services.mastery_model import MasteryModelService


@pytest.mark.asyncio
async def test_semantic_evaluation():
    evaluator = EvaluatorAgent()
    
    # Test correct answer
    res_correct = await evaluator.evaluate_student_answer(
        concept="Newton's First Law",
        question_prompt="Why does the passenger move forward when braking?",
        expected_answer="Inertia of motion causes the body to continue moving forward.",
        student_answer="Because of inertia of motion, the passenger continues moving."
    )
    assert res_correct.is_correct is True
    assert res_correct.score >= 0.8

    # Test misconception answer
    res_wrong = await evaluator.evaluate_student_answer(
        concept="Newton's First Law",
        question_prompt="Why does the passenger move forward when braking?",
        expected_answer="Inertia of motion causes the body to continue moving forward.",
        student_answer="Because friction pulls them forward and gravity increases when braking."
    )
    assert res_wrong.is_correct is False
    assert res_wrong.score < 0.5


@pytest.mark.asyncio
async def test_misconception_diagnosis():
    misc_agent = MisconceptionAgent()
    res = await misc_agent.diagnose_misconception(
        concept="Ohm's Law",
        question_prompt="What happens to current if resistance increases?",
        expected_answer="Current decreases proportionally.",
        student_answer="Current increases with resistance because more resistance generates more power."
    )
    assert res.detected is True
    assert res.pedagogical_analogy is not None


def test_deterministic_adaptation_policy():
    engine = AdaptationEngine()
    
    # When score is low, must trigger reteach
    from app.schemas.interaction import AnswerEvaluationResult, MisconceptionResult
    eval_res = AnswerEvaluationResult(
        is_correct=False,
        score=0.2,
        confidence=0.9,
        feedback="Incorrect intuition.",
        missing_concepts=["Inertia"],
        reasoning_quality="poor"
    )
    misc_res = MisconceptionResult(
        detected=True,
        root_cause="Aristotelian motion fallacy",
        misconception_title="Motion requires continuous force",
        severity="medium",
        pedagogical_analogy="Think of frictionless ice rink.",
        recommended_reteach_strategy="Frictionless surface demo"
    )
    decision = engine.decide_next_action(eval_res, misc_res, "Newton's First Law", {"analogy": "Ice rink"})
    assert decision.action == "reteach"
    assert "remedial_explanation" in decision.model_dump()
    assert decision.next_question is not None


def test_mastery_model_formula(db_session):
    mastery_service = MasteryModelService(db_session)
    score = mastery_service.calculate_interaction_mastery(
        correctness_score=1.0,
        attempts=2,
        correct_attempts=2,
        difficulty="intermediate",
        reasoning_quality="excellent"
    )
    assert score >= 80.0
