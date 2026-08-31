from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_text: str
    page_number: int
    section_title: str
    relevance_score: Optional[float] = None
    chunk_metadata: Dict[str, Any] = {}


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    language: str
    processing_status: str
    page_count: int
    doc_metadata: Dict[str, Any] = {}
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []


class RAGQueryRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    top_k: int = 4
    language: str = "en"


class RAGQueryResponse(BaseModel):
    query: str
    is_grounded_in_docs: bool
    source_type: str  # "uploaded_document" or "general_knowledge"
    chunks: List[DocumentChunkResponse] = []
    answer: str
    grounding_notes: Optional[str] = None
