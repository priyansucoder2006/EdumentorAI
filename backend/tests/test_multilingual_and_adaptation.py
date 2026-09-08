import pytest
from app.services.language_adapter import LanguageAdapterService
from app.services.adaptation_engine import AdaptationEngine
from app.ai.agents.recommender_agent import RecommenderAgent
from app.schemas.interaction import AnswerEvaluationResult, MisconceptionResult
from app.models.lesson import Lesson, LessonStep


@pytest.mark.asyncio
async def test_multilingual_translation_preserves_formulas():
    adapter = LanguageAdapterService()
    
    text = "In physics, force is calculated as $F = ma$, and energy is given by $E = mc^2$ with code `calculateForce(m, a)`."
    translated = await adapter.translate_text(text, "hinglish", "Physics")
    
    # Mathematical formulas and code tokens MUST be intact in the output
    assert "$F = ma$" in translated, f"Formula $F = ma$ was corrupted in: {translated}"
    assert "$E = mc^2$" in translated, f"Formula $E = mc^2$ was corrupted in: {translated}"
    assert "`calculateForce(m, a)`" in translated, f"Code token was corrupted in: {translated}"


def test_dynamic_adaptation_on_biology_topic():
    engine = AdaptationEngine()

    eval_result = AnswerEvaluationResult(
        is_correct=False,
        score=0.25,
        confidence=0.95,
        feedback="Incorrect. Oxygen released during photosynthesis comes from water, not CO2.",
        missing_concepts=["Photolysis of water", "Photosystem II"],
        reasoning_quality="poor"
    )

    misc_result = MisconceptionResult(
        detected=True,
        root_cause="Student assumed oxygen is produced by stripping carbon from carbon dioxide.",
        misconception_title="Source of Photosynthetic Oxygen Gas",
        severity="medium",
        pedagogical_analogy="Solar panels using water as the electron donor source.",
        recommended_reteach_strategy="Photolysis visual diagram."
    )

    decision = engine.decide_next_action(
        evaluation=eval_result,
        misconception=misc_result,
        current_step_concept="Light-Dependent Photolysis",
        current_step_data={
            "explanation": "Light energy splits H2O molecules into protons, electrons, and O2 gas.",
            "example": "Isotope labeling with Oxygen-18 proves O2 comes from water.",
            "analogy": "A water mill turning to generate electricity while releasing pure spray."
        },
        attempts_on_step=1
    )

    assert decision.action in ["reteach", "simplify", "provide_analogy"]
    assert "Photolysis" in decision.rationale or "Oxygen" in decision.rationale
    assert decision.next_question is not None
    # Crucially: ensure NO Newton strings are present!
    assert "friction" not in decision.rationale.lower()
    assert "inertia" not in decision.rationale.lower()
    assert "newton" not in decision.rationale.lower()


@pytest.mark.asyncio
async def test_dynamic_recommender_on_arbitrary_topic():
    recommender = RecommenderAgent()
    
    recs = await recommender.generate_recommendations(
        topic="Organic Chemistry: Reaction Mechanisms",
        overall_mastery=45.0,
        weak_concepts=["Nucleophilic Substitution SN1 vs SN2"],
        strong_concepts=["Alkane Halogenation"],
        misconceptions=["Confusing carbocation stability with transition state energy"]
    )

    assert len(recs) >= 3
    # Check revision recommendation targets the specific weak concept
    assert recs[0].type == "revision"
    assert "SN1 vs SN2" in recs[0].concept or "Organic Chemistry" in recs[0].topic
    assert recs[1].type == "next_topic"
    assert len(recs[1].topic) > 3
    assert recs[2].type == "practice_problem"
