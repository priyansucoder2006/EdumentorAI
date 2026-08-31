from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import RAGQueryRequest, RAGQueryResponse
from app.ai.agents.rag_agent import RAGAgent
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    rag_in: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = RAGAgent(db)
    result = await agent.retrieve_knowledge(
        query=rag_in.query,
        document_id=rag_in.document_id,
        user_id=current_user.id,
        top_k=rag_in.top_k
    )
    return result
