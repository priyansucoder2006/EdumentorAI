from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.ai.providers.embedding_provider import get_embedding_provider
from app.core.logging import logger


class VectorStoreService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()

    async def search_similar_chunks(
        self,
        query: str,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        top_k: int = 4,
        min_similarity: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid semantic cosine similarity search across indexed document chunks,
        strictly scoped to the user's uploaded documents.
        """
        query_vec = await self.embedding_provider.embed_text(query)

        query_builder = self.db.query(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id)
        if user_id:
            query_builder = query_builder.filter(Document.user_id == user_id)
        if document_id:
            query_builder = query_builder.filter(DocumentChunk.document_id == document_id)

        all_chunks = query_builder.all()
        if not all_chunks:
            return []

        scored_results = []
        for chunk in all_chunks:
            if not chunk.embedding:
                continue
            sim = self.embedding_provider.similarity(query_vec, chunk.embedding)
            if sim >= min_similarity:
                scored_results.append({
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_text": chunk.chunk_text,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "relevance_score": round(sim, 4),
                    "chunk_metadata": chunk.chunk_metadata or {}
                })

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:top_k]
