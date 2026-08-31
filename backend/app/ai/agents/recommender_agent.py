from typing import List, Dict, Any, Optional
from app.ai.providers import get_llm_provider
from app.ai.prompts.visual import RECOMMENDATION_SYSTEM_PROMPT
from app.schemas.progress import RecommendationItem
from app.core.logging import logger


class RecommenderAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def generate_recommendations(
        self,
        topic: str,
        overall_mastery: float,
        weak_concepts: List[str],
        strong_concepts: List[str],
        misconceptions: List[str]
    ) -> List[RecommendationItem]:
        """
        Generates targeted pedagogical recommendations based on mastery and diagnosed misconceptions.
        """
        recommendations = []

        # 1. Revision Recommendation if mastery < 70 or weak concepts present
        if weak_concepts or overall_mastery < 70.0:
            primary_weak = weak_concepts[0] if weak_concepts else topic
            reason = f"Mastery is currently {round(overall_mastery, 1)}%. Reinforcing '{primary_weak}' will build a rock-solid foundation."
            if misconceptions:
                reason += f" Review the analogy for: {misconceptions[0]}."
            
            recommendations.append(
                RecommendationItem(
                    type="revision",
                    topic=topic,
                    concept=primary_weak,
                    reason=reason,
                    suggested_difficulty="beginner" if overall_mastery < 50 else "intermediate",
                    estimated_minutes=10
                )
            )

        # 2. Next Topic Recommendation
        next_topic_map = {
            "Newton's Laws of Motion": "Work, Energy, and Conservation of Momentum",
            "React Components & State Management": "React Hooks (useEffect, useMemo) & Custom Hooks",
            "Ohm's Law & Electric Circuits": "Kirchhoff's Laws and Circuit Mesh Analysis",
            "Machine Learning Fundamentals": "Supervised Classification (Logistic Regression & Decision Trees)"
        }
        next_topic = next_topic_map.get(topic, f"Advanced Topics in {topic}")
        recommendations.append(
            RecommendationItem(
                type="next_topic",
                topic=next_topic,
                concept="Module 2 Progression",
                reason=f"Natural curriculum progression following mastery of '{topic}'.",
                suggested_difficulty="intermediate" if overall_mastery >= 70 else "beginner",
                estimated_minutes=20
            )
        )

        # 3. Practice Drill Recommendation
        recommendations.append(
            RecommendationItem(
                type="practice_problem",
                topic=topic,
                concept="Applied Problem Solving",
                reason="Practice 3 interactive challenge problems to solidify retention.",
                suggested_difficulty="advanced" if overall_mastery >= 85 else "intermediate",
                estimated_minutes=5
            )
        )

        return recommendations
