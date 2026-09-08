from typing import List, Dict, Any, Optional
from app.ai.providers import get_llm_provider
from app.schemas.progress import RecommendationItem
from app.core.logging import logger


class RecommenderAgent:
    """
    Dynamic Pedagogical Recommender Agent.
    Synthesizes actionable next steps for ANY subject based on learner mastery,
    diagnosed misconceptions, weak concepts, and prerequisites.
    Generates: NEXT_TOPIC, REVISION_TOPIC, PRACTICE_PROBLEM, and ADVANCED_TOPIC.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def generate_recommendations(
        self,
        topic: str,
        overall_mastery: float,
        weak_concepts: List[str],
        strong_concepts: List[str],
        misconceptions: List[str] = [],
        learning_goal: str = "mastery",
        difficulty: str = "intermediate"
    ) -> List[RecommendationItem]:
        recommendations: List[RecommendationItem] = []

        # 1. REVISION RECOMMENDATION: If weak concepts exist or mastery < 70%
        if weak_concepts or overall_mastery < 70.0:
            target_weak = weak_concepts[0] if weak_concepts else f"Foundational {topic}"
            reason = f"Mastery is currently {round(overall_mastery, 1)}%. Reinforcing '{target_weak}' will solidify your core intuition before progressing."
            if misconceptions:
                reason += f" Review the intuitive analogy addressing: {misconceptions[0]}."

            recommendations.append(
                RecommendationItem(
                    type="revision",
                    topic=topic,
                    concept=target_weak,
                    reason=reason,
                    suggested_difficulty="beginner" if overall_mastery < 50 else "intermediate",
                    estimated_minutes=10
                )
            )

        # 2. NEXT TOPIC / CURRICULUM PROGRESSION RECOMMENDATION
        # Dynamically infer the natural next module for the subject
        next_topic = await self._infer_next_topic(topic, strong_concepts)
        recommendations.append(
            RecommendationItem(
                type="next_topic",
                topic=next_topic,
                concept="Next Curriculum Module",
                reason=f"Natural sequential progression following mastery of '{topic}'.",
                suggested_difficulty="intermediate" if overall_mastery >= 70 else "beginner",
                estimated_minutes=20
            )
        )

        # 3. PRACTICE PROBLEM / DRILL RECOMMENDATION
        recommendations.append(
            RecommendationItem(
                type="practice_problem",
                topic=topic,
                concept=strong_concepts[0] if strong_concepts else topic,
                reason="Complete interactive problem-solving challenges to build procedural fluency and long-term retention.",
                suggested_difficulty="advanced" if overall_mastery >= 85 else "intermediate",
                estimated_minutes=5
            )
        )

        # 4. ADVANCED TOPIC RECOMMENDATION: If student shows high mastery
        if overall_mastery >= 85.0:
            recommendations.append(
                RecommendationItem(
                    type="advanced_topic",
                    topic=f"Advanced Applications & Edge Cases in {topic}",
                    concept="Higher-Order Analysis",
                    reason="Demonstrated exceptional conceptual clarity. Challenge yourself with real-world edge cases.",
                    suggested_difficulty="advanced",
                    estimated_minutes=30
                )
            )

        return recommendations

    async def _infer_next_topic(self, topic: str, strong_concepts: List[str]) -> str:
        prompt = f"""Given the subject topic '{topic}' and mastered concepts [{', '.join(strong_concepts)}], what is the single most logical next topic in a standard academic curriculum?
Respond with ONLY the topic title (2 to 6 words), nothing else."""
        try:
            res = await self.llm.generate_text(prompt, system_prompt="You are an expert curriculum architect.")
            cleaned = res.strip().strip('"').strip("'")
            if cleaned and len(cleaned) < 80:
                return cleaned
        except Exception:
            pass
        return f"Advanced Systems in {topic}"
