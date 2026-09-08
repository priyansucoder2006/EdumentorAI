import uuid
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.learning_progress import LearningProgress
from app.models.learning_path import LearningPath
from app.models.lesson import Lesson
from app.schemas.progress import (
    MasteryOverviewResponse,
    ConceptMasteryItem,
    LearningPathResponse,
    RoadmapGenerateRequest,
    NodeStatusUpdateRequest
)
from app.ai.providers import get_llm_provider
from app.api.deps import get_current_user
from app.core.logging import logger

router = APIRouter()


@router.get("", response_model=MasteryOverviewResponse)
def get_overall_mastery(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_progress = db.query(LearningProgress).filter(LearningProgress.user_id == current_user.id).all()
    
    if not all_progress:
        return MasteryOverviewResponse(
            overall_mastery=0.0,
            total_topics_studied=0,
            total_concepts_learned=0,
            strong_topics=[],
            weak_topics=[],
            concept_details=[]
        )

    topics_set = {p.topic for p in all_progress}
    avg_mastery = sum(p.mastery_score for p in all_progress) / len(all_progress)
    strong = [p.concept for p in all_progress if p.mastery_score >= 75.0]
    weak = [p.concept for p in all_progress if p.mastery_score < 50.0]

    return MasteryOverviewResponse(
        overall_mastery=round(avg_mastery, 1),
        total_topics_studied=len(topics_set),
        total_concepts_learned=len(all_progress),
        strong_topics=strong[:10],
        weak_topics=weak[:10],
        concept_details=all_progress
    )


@router.post("/paths/generate", response_model=LearningPathResponse)
async def generate_custom_roadmap(
    req: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dynamically generates a comprehensive, time-allocated curriculum roadmap
    (e.g., '6 Months of Data Science', '3 Months of Web Dev', '1 Year of AI Engineering')
    specifying exact month/week allocations, hours per week, concepts, and milestone projects.
    """
    topic = req.topic.strip()
    duration_label = req.duration_label or f"{req.duration_months or 6} Months"
    hours_per_week = req.hours_per_week or 10
    level = req.current_level or "beginner"
    goal = req.learning_goal or "career"

    num_stages = max(3, min(8, req.duration_months or 6))

    prompt = f"""You are a world-class educational curriculum architect.
Design a highly detailed, professional, structured learning roadmap for:
- Subject/Field: {topic}
- Target Timeline: {duration_label} ({num_stages} distinct phases/months)
- Time Commitment: {hours_per_week} hours per week
- Current Level: {level.upper()}
- Primary Goal: {goal.upper()}

Return a JSON array of {num_stages} phase objects with this EXACT structure:
[
  {{
    "id": "node_1",
    "phase_name": "Month 1 (Weeks 1-4): Foundations of {topic}",
    "time_commitment": "{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
    "title": "Clear Module Title (3-6 words)",
    "description": "Comprehensive summary of what the student will master in this stage.",
    "difficulty": "beginner",
    "concepts": [
      "Specific Concept 1",
      "Specific Concept 2",
      "Specific Concept 3",
      "Specific Concept 4"
    ],
    "practical_project": "Name & description of practical project or portfolio asset built in this stage",
    "tools_and_resources": ["Tool 1", "Tool 2", "Library/Resource 3"],
    "prerequisites": ["None or prior stage"]
  }}
]

CRITICAL:
1. Provide rich, concrete, subject-specific details for {topic}.
2. Break down exactly what to learn, how much time to give, and what to build.
3. Return ONLY the valid JSON array, no markdown fences or conversational text."""

    llm = get_llm_provider()
    nodes: List[Dict[str, Any]] = []

    try:
        raw_res = await llm.generate_text(prompt, system_prompt="You are a professional curriculum architect.")
        json_str = raw_res.strip()
        if "[" in json_str and "]" in json_str:
            json_str = json_str[json_str.find("["):json_str.rfind("]")+1]
            parsed_nodes = json.loads(json_str)
            for idx, pn in enumerate(parsed_nodes):
                status_val = "in_progress" if idx == 0 else "locked"
                prog_val = 15 if idx == 0 else 0
                nodes.append({
                    "id": pn.get("id", f"node_{idx+1}"),
                    "phase_name": pn.get("phase_name", f"Stage {idx+1} ({hours_per_week} hrs/week)"),
                    "time_commitment": pn.get("time_commitment", f"{hours_per_week} hrs/week"),
                    "title": pn.get("title", f"Stage {idx+1}: {topic}"),
                    "description": pn.get("description", f"Master core competencies in {topic}."),
                    "difficulty": pn.get("difficulty", "intermediate"),
                    "status": status_val,
                    "progress": prog_val,
                    "concepts": pn.get("concepts", [f"{topic} core fundamentals"]),
                    "practical_project": pn.get("practical_project", f"Practical {topic} capstone application"),
                    "tools_and_resources": pn.get("tools_and_resources", ["Core SDK", "Interactive Practice"]),
                    "prerequisites": pn.get("prerequisites", [])
                })
    except Exception as e:
        logger.warning(f"Curriculum generation fallback for {topic}: {e}")
        # Robust fallback for Data Science and generic subjects
        if "data science" in topic.lower():
            nodes = [
                {
                    "id": "node_1",
                    "phase_name": f"Month 1 (Weeks 1-4): Python & Math Foundations",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                    "title": "Python Programming & Mathematics for Data Science",
                    "description": "Master Python data structures, NumPy vectorization, Pandas wrangling, and essential linear algebra and calculus.",
                    "difficulty": "beginner",
                    "status": "in_progress",
                    "progress": 25,
                    "concepts": ["NumPy Arrays & Linear Algebra", "Pandas DataFrames & Data Cleaning", "Descriptive & Inferential Statistics", "Probability Distributions & Hypothesis Testing"],
                    "practical_project": "Exploratory Data Analysis (EDA) on World Economic / Demographics Dataset",
                    "tools_and_resources": ["Python 3.12", "JupyterLab", "Pandas", "Matplotlib", "Seaborn"],
                    "prerequisites": ["Basic computer literacy"]
                },
                {
                    "id": "node_2",
                    "phase_name": f"Month 2 (Weeks 5-8): SQL & Advanced Data Visualization",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                    "title": "Relational Databases, SQL & Interactive Dashboards",
                    "description": "Write complex SQL queries with window functions and CTEs, and build interactive analytical dashboards.",
                    "difficulty": "intermediate",
                    "status": "locked",
                    "progress": 0,
                    "concepts": ["PostgreSQL & Relational Schema Design", "Complex Joins, Subqueries & Window Functions", "Aggregation CTEs & Performance Indexing", "Interactive Storytelling with Plotly & Streamlit"],
                    "practical_project": "End-to-End E-Commerce Customer Analytics Dashboard with Live SQL Backend",
                    "tools_and_resources": ["PostgreSQL", "DBeaver", "Plotly", "Streamlit"],
                    "prerequisites": ["Month 1: Python Foundations"]
                },
                {
                    "id": "node_3",
                    "phase_name": f"Month 3 (Weeks 9-12): Classical Machine Learning",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                    "title": "Supervised & Unsupervised Machine Learning",
                    "description": "Implement regression, classification, clustering, and ensemble algorithms with rigorous evaluation.",
                    "difficulty": "intermediate",
                    "status": "locked",
                    "progress": 0,
                    "concepts": ["Linear & Logistic Regression", "Decision Trees, Random Forests & Gradient Boosting", "K-Means Clustering & Dimensionality Reduction (PCA)", "Cross-Validation, Regularization & ROC-AUC Metrics"],
                    "practical_project": "Customer Churn Prediction & Risk Scoring Pipeline with XGBoost",
                    "tools_and_resources": ["Scikit-Learn", "XGBoost", "LightGBM", "Imbalanced-Learn"],
                    "prerequisites": ["Month 1 & 2 Foundations"]
                },
                {
                    "id": "node_4",
                    "phase_name": f"Month 4 (Weeks 13-16): Deep Learning & Neural Networks",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                    "title": "Deep Neural Networks & Computer Vision",
                    "description": "Build feedforward neural networks, convolutional architectures, and transfer learning pipelines in PyTorch.",
                    "difficulty": "advanced",
                    "status": "locked",
                    "progress": 0,
                    "concepts": ["Perceptrons, Backpropagation & Optimizers (Adam/SGD)", "Convolutional Neural Networks (CNNs)", "Transfer Learning with ResNet & EfficientNet", "Overfitting Mitigation (Dropout, BatchNorm)"],
                    "practical_project": "Medical Image / Object Classification Model in PyTorch",
                    "tools_and_resources": ["PyTorch", "Torchvision", "TensorBoard", "Google Colab GPU"],
                    "prerequisites": ["Month 3: Machine Learning"]
                },
                {
                    "id": "node_5",
                    "phase_name": f"Month 5 (Weeks 17-20): NLP, LLMs & Retrieval Augmented Gen",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                    "title": "Natural Language Processing, Transformers & RAG",
                    "description": "Master tokenization, transformer self-attention mechanisms, HuggingFace, and RAG architectures.",
                    "difficulty": "advanced",
                    "status": "locked",
                    "progress": 0,
                    "concepts": ["Word Embeddings (Word2Vec, BGE-M3)", "Transformer Architecture & Multi-Head Self-Attention", "Vector Databases & Hybrid Dense/Sparse Retrieval", "Prompt Engineering & RAG Pipeline Orchestration"],
                    "practical_project": "Document Question-Answering RAG Assistant over Enterprise Reports",
                    "tools_and_resources": ["HuggingFace", "LangChain", "Qdrant / ChromaDB", "FastAPI"],
                    "prerequisites": ["Month 4: Deep Learning"]
                },
                {
                    "id": "node_6",
                    "phase_name": f"Month 6 (Weeks 21-24): MLOps, Deployment & Capstone",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                    "title": "Production MLOps, Model Serving & Portfolio Capstone",
                    "description": "Package models into REST APIs, Docker containerization, CI/CD automated deployment, and portfolio showcase.",
                    "difficulty": "advanced",
                    "status": "locked",
                    "progress": 0,
                    "concepts": ["Model Serialization (ONNX, Joblib)", "FastAPI High-Performance Inference Endpoints", "Docker Containerization & Microservices", "Monitoring, Drift Detection & Portfolio Presentation"],
                    "practical_project": "Full Production-Grade AI Microservice with Web UI & Live Cloud Deployment",
                    "tools_and_resources": ["Docker", "FastAPI", "GitHub Actions", "AWS / Render"],
                    "prerequisites": ["Months 1-5"]
                }
            ]
        else:
            for idx in range(num_stages):
                status_val = "in_progress" if idx == 0 else "locked"
                nodes.append({
                    "id": f"node_{idx+1}",
                    "phase_name": f"Month {idx+1} (Weeks {idx*4+1}-{idx*4+4})",
                    "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week*4} hours total",
                    "title": f"Stage {idx+1}: {topic} Core Module",
                    "description": f"Targeted competencies and practical exercises for stage {idx+1} of {topic}.",
                    "difficulty": "beginner" if idx == 0 else ("intermediate" if idx < num_stages - 1 else "advanced"),
                    "status": status_val,
                    "progress": 20 if idx == 0 else 0,
                    "concepts": [f"{topic} Core Principles Part {idx+1}", f"Practical Problem Solving in Stage {idx+1}"],
                    "practical_project": f"Milestone Project {idx+1}: Applied {topic} Portfolio System",
                    "tools_and_resources": ["Interactive Practice", "Documentation", "Project Sandbox"],
                    "prerequisites": [f"Stage {idx}"] if idx > 0 else ["Foundational literacy"]
                })

    new_path = LearningPath(
        user_id=current_user.id,
        topic=f"{topic} — {duration_label} Roadmap",
        description=f"Comprehensive {duration_label} curriculum for {topic} ({hours_per_week} hrs/week) tailored for {level} learners targeting {goal}.",
        nodes=nodes,
        current_node_id=nodes[0]["id"] if nodes else None,
        status="active",
        progress_percentage=round(sum(n.get("progress", 0) for n in nodes) / len(nodes)) if nodes else 0
    )
    db.add(new_path)
    db.commit()
    db.refresh(new_path)
    return new_path


@router.get("/paths", response_model=List[LearningPathResponse])
def get_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    paths = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).order_by(LearningPath.created_at.desc()).all()
    return paths


@router.get("/paths/{path_id}", response_model=LearningPathResponse)
def get_single_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = db.query(LearningPath).filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")
    return path


@router.put("/paths/{path_id}/node/{node_id}", response_model=LearningPathResponse)
def update_node_status(
    path_id: str,
    node_id: str,
    req: NodeStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = db.query(LearningPath).filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")

    nodes = list(path.nodes or [])
    node_found = False

    for idx, n in enumerate(nodes):
        if n.get("id") == node_id:
            node_found = True
            n["status"] = req.status
            if req.status == "completed":
                n["progress"] = 100
                # Unlock next node if present
                if idx + 1 < len(nodes) and nodes[idx + 1].get("status") == "locked":
                    nodes[idx + 1]["status"] = "in_progress"
                    nodes[idx + 1]["progress"] = 10
            elif req.progress is not None:
                n["progress"] = req.progress
            break

    if not node_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found in learning path.")

    path.nodes = nodes
    path.progress_percentage = round(sum(n.get("progress", 0) for n in nodes) / len(nodes)) if nodes else 0
    if path.progress_percentage >= 100:
        path.status = "completed"

    db.commit()
    db.refresh(path)
    return path


@router.delete("/paths/{path_id}")
def delete_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = db.query(LearningPath).filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")

    db.delete(path)
    db.commit()
    return {"message": "Learning path deleted successfully."}


@router.get("/{topic}", response_model=List[ConceptMasteryItem])
def get_topic_progress(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.topic.ilike(f"%{topic}%")
    ).all()
    return progress
