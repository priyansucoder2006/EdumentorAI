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


def build_curriculum_nodes(topic: str, num_stages: int = 6, hours_per_week: int = 10) -> List[Dict[str, Any]]:
    clean_topic = topic.split("—")[0].strip() if "—" in topic else topic.strip()
    low = clean_topic.lower()

    if "data science" in low or "machine learning" in low:
        return [
            {
                "id": "node_1",
                "phase_name": f"Month 1 (Weeks 1-4): Python & Math Foundations",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Python Programming & Mathematics for Data Science",
                "description": "Master Python data structures, NumPy vectorization, Pandas wrangling, and essential linear algebra and calculus.",
                "difficulty": "beginner",
                "status": "in_progress",
                "progress": 35,
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
                "phase_name": f"Month 5 (Weeks 17-20): NLP, Transformers & RAG",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Natural Language Processing, LLMs & Retrieval Augmented Gen",
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

    elif "web" in low or "react" in low or "frontend" in low or "full-stack" in low or "full stack" in low:
        return [
            {
                "id": "node_1",
                "phase_name": f"Month 1 (Weeks 1-4): Modern JavaScript & HTML/CSS",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "ES6+ JavaScript, DOM Manipulation & Modern CSS",
                "description": "Master async/await, closures, prototypes, Flexbox, CSS Grid, and responsive UI design.",
                "difficulty": "beginner",
                "status": "in_progress",
                "progress": 40,
                "concepts": ["Asynchronous JavaScript (Promises & Fetch)", "Modern DOM & Event Propagation", "CSS Grid & Flexbox Layout Systems", "Tailwind CSS & Responsive Design"],
                "practical_project": "Interactive Kanban / Task Management Web App",
                "tools_and_resources": ["VS Code", "Node.js", "Chrome DevTools", "Tailwind CSS"],
                "prerequisites": ["Basic HTML/CSS basics"]
            },
            {
                "id": "node_2",
                "phase_name": f"Month 2 (Weeks 5-8): React 18 & State Architecture",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Component Design, Hooks & Client-Side Routing",
                "description": "Build high-performance single page applications with React, custom hooks, and React Router.",
                "difficulty": "intermediate",
                "status": "locked",
                "progress": 0,
                "concepts": ["Component Lifecycle & Custom Hooks", "Context API & TanStack React Query", "React Router v6 Protected Route Patterns", "Monaco Code Editor & Canvas Integration"],
                "practical_project": "Full-Featured Student Interactive Learning Dashboard",
                "tools_and_resources": ["React 18", "Vite", "React Router", "Lucide Icons"],
                "prerequisites": ["Month 1: JavaScript Foundations"]
            },
            {
                "id": "node_3",
                "phase_name": f"Month 3 (Weeks 9-12): Backend APIs & Database Persistence",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Node.js / Express & FastAPI REST Architectures",
                "description": "Develop authenticated REST APIs with JWT security, relational databases, and data validation.",
                "difficulty": "intermediate",
                "status": "locked",
                "progress": 0,
                "concepts": ["RESTful Resource Design & Middleware", "JWT Authentication & Role-Based Access", "PostgreSQL / SQLite ORM Integration", "File Uploads, Streams & Background Workers"],
                "practical_project": "Full-Stack Collaborative Classroom Platform with Live API",
                "tools_and_resources": ["FastAPI", "Express", "SQLAlchemy", "PostgreSQL"],
                "prerequisites": ["Month 2: React Core"]
            },
            {
                "id": "node_4",
                "phase_name": f"Month 4 (Weeks 13-16): Cloud Deployment & Production CI/CD",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Dockerization, WebSockets & Production Cloud Hosting",
                "description": "Containerize full-stack apps and deploy to production cloud providers with automated CI/CD.",
                "difficulty": "advanced",
                "status": "locked",
                "progress": 0,
                "concepts": ["Docker Multi-Stage Container Builds", "Real-Time WebSockets Communication", "Cloud Deployment on Render & AWS", "SSL/TLS, CORS & Security Hardening"],
                "practical_project": "Live Scalable SaaS Web Platform with Real-Time Communication",
                "tools_and_resources": ["Docker", "Render", "GitHub Actions", "WebSockets"],
                "prerequisites": ["Months 1-3"]
            }
        ]

    elif "devops" in low or "cloud" in low or "aws" in low:
        return [
            {
                "id": "node_1",
                "phase_name": f"Month 1 (Weeks 1-4): Linux & Scripting Automation",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Linux Kernel Internals, Bash Scripting & Networking",
                "description": "Master command-line productivity, processes, systemd services, SSH keys, and TCP/IP networking.",
                "difficulty": "beginner",
                "status": "in_progress",
                "progress": 25,
                "concepts": ["Linux Filesystem & User Permissions", "Bash Shell Scripting & Cron Jobs", "Networking: DNS, Subnets & Firewalls", "Git Version Control & Branching Workflows"],
                "practical_project": "Automated Server Health Monitoring & Alerting Daemon",
                "tools_and_resources": ["Ubuntu Server", "Bash", "systemd", "Wireshark"],
                "prerequisites": ["Basic computer literacy"]
            },
            {
                "id": "node_2",
                "phase_name": f"Month 2 (Weeks 5-8): Containerization with Docker",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Docker Containers, Multi-Stage Builds & Docker Compose",
                "description": "Package applications into isolated, reproducible container environments with networked services.",
                "difficulty": "intermediate",
                "status": "locked",
                "progress": 0,
                "concepts": ["Docker Engine Architecture & Namespaces", "Writing Optimal Multi-Stage Dockerfiles", "Docker Compose Multi-Container Orchestration", "Volume Mounts & Container Security Hardening"],
                "practical_project": "Containerized 3-Tier Web Stack with PostgreSQL & Redis Caching",
                "tools_and_resources": ["Docker", "Docker Compose", "Docker Hub"],
                "prerequisites": ["Month 1: Linux Foundations"]
            },
            {
                "id": "node_3",
                "phase_name": f"Month 3 (Weeks 9-12): CI/CD & AWS Cloud Architecture",
                "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
                "title": "Continuous Integration, Delivery & Cloud Infrastructure",
                "description": "Build automated GitHub Actions deployment pipelines and provision AWS VPC, EC2, and S3 resources.",
                "difficulty": "advanced",
                "status": "locked",
                "progress": 0,
                "concepts": ["GitHub Actions Automated Test & Deploy Pipelines", "AWS VPC, EC2, IAM Security & S3 Buckets", "Infrastructure as Code with Terraform Basics", "Log Aggregation, Prometheus & Grafana Monitoring"],
                "practical_project": "Automated Zero-Downtime CI/CD Pipeline to AWS Cloud",
                "tools_and_resources": ["GitHub Actions", "AWS", "Terraform", "Grafana"],
                "prerequisites": ["Months 1 & 2"]
            }
        ]

    # Dynamic structured curriculum for ANY other topic
    stages_to_build = max(3, min(6, num_stages))
    result = []
    milestone_names = [
        "Foundational Principles & Core Concepts",
        "Applied Methods, Tooling & Practical Workflows",
        "Intermediate Problem Solving & Core Architecture",
        "Advanced Case Studies & Real-World Integration",
        "Performance Optimization, Scaling & Refinement",
        "Comprehensive Capstone Showcase & Portfolio Project"
    ]
    difficulties = ["beginner", "beginner", "intermediate", "intermediate", "advanced", "advanced"]

    for idx in range(stages_to_build):
        stg_num = idx + 1
        status_val = "in_progress" if idx == 0 else "locked"
        prog_val = 25 if idx == 0 else 0
        diff = difficulties[min(idx, len(difficulties)-1)]
        title = f"{clean_topic}: {milestone_names[min(idx, len(milestone_names)-1)]}"

        result.append({
            "id": f"node_{stg_num}",
            "phase_name": f"Stage {stg_num} (Weeks {idx*4+1}-{idx*4+4})",
            "time_commitment": f"{hours_per_week} hrs/week • {hours_per_week * 4} hours total",
            "title": title,
            "description": f"Deep dive into {clean_topic} stage {stg_num}, focusing on practical mastery, core competencies, and verifiable hands-on knowledge.",
            "difficulty": diff,
            "status": status_val,
            "progress": prog_val,
            "concepts": [
                f"{clean_topic} Core Concept {stg_num}.1",
                f"{clean_topic} Analytical Method {stg_num}.2",
                f"{clean_topic} Applied Problem Solving {stg_num}.3",
                f"{clean_topic} Professional Best Practices {stg_num}.4"
            ],
            "practical_project": f"Stage {stg_num} Milestone Project: Applied {clean_topic} Portfolio Solution",
            "tools_and_resources": [f"{clean_topic} Studio", "Interactive Practice Sandbox", "Reference Manual"],
            "prerequisites": [f"Stage {idx}"] if idx > 0 else ["Foundational literacy"]
        })
    return result


@router.post("/paths/generate", response_model=LearningPathResponse)
async def generate_custom_roadmap(
    req: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dynamically generates a comprehensive, time-allocated curriculum roadmap
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
            if isinstance(parsed_nodes, list) and len(parsed_nodes) > 0:
                for idx, pn in enumerate(parsed_nodes):
                    status_val = "in_progress" if idx == 0 else "locked"
                    prog_val = 20 if idx == 0 else 0
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
        logger.warning(f"Curriculum generation fallback triggered for {topic}: {e}")

    # Guaranteed fail-safe: If LLM did not return parsed nodes, build domain architect curriculum
    if not nodes:
        nodes = build_curriculum_nodes(topic=topic, num_stages=num_stages, hours_per_week=hours_per_week)

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
    # Auto-heal any existing roadmaps in database that have empty nodes
    updated = False
    for p in paths:
        if not p.nodes or len(p.nodes) == 0:
            p.nodes = build_curriculum_nodes(topic=p.topic, num_stages=6, hours_per_week=10)
            p.current_node_id = p.nodes[0]["id"] if p.nodes else None
            p.progress_percentage = 20
            updated = True
    if updated:
        try:
            db.commit()
            for p in paths:
                db.refresh(p)
        except Exception as ex:
            db.rollback()
            logger.warning(f"Error auto-healing legacy learning paths: {ex}")
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
    if not path.nodes or len(path.nodes) == 0:
        path.nodes = build_curriculum_nodes(topic=path.topic, num_stages=6, hours_per_week=10)
        path.current_node_id = path.nodes[0]["id"] if path.nodes else None
        path.progress_percentage = 20
        db.commit()
        db.refresh(path)
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
