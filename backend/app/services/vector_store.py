from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.ai.providers.embedding_provider import get_embedding_provider
from app.services.hybrid_retriever import BM25Retriever, reciprocal_rank_fusion
from app.core.logging import logger


class VectorStoreService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()
        self.bm25_retriever = BM25Retriever(k1=1.5, b=0.75)

    async def search_similar_chunks(
        self,
        query: str,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        top_k: int = 4,
        min_similarity: float = 0.10
    ) -> List[Dict[str, Any]]:
        """
        Executes true Hybrid RAG search across user document chunks:
        1. Dense Vector semantic cosine similarity search.
        2. Sparse BM25 keyword matching with inverted token statistics.
        3. Reciprocal Rank Fusion (RRF) candidate reranking.
        """
        # Fetch candidate chunks from DB scoped by user / document
        query_builder = self.db.query(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id)
        if user_id:
            query_builder = query_builder.filter(Document.user_id == user_id)
        if document_id:
            query_builder = query_builder.filter(DocumentChunk.document_id == document_id)

        all_chunks = query_builder.all()
        if not all_chunks:
            return []

        # Convert to dictionary format
        chunk_dicts = [
            {
                "id": str(c.id),
                "document_id": str(c.document_id),
                "chunk_text": c.chunk_text,
                "page_number": c.page_number,
                "section_title": c.section_title or f"Page {c.page_number}",
                "embedding": c.embedding,
                "chunk_metadata": c.chunk_metadata or {}
            }
            for c in all_chunks
        ]

        # 1. Dense Semantic Vector Search
        query_vec = await self.embedding_provider.embed_text(query)
        vector_ranked = []
        for c in chunk_dicts:
            if not c.get("embedding"):
                continue
            sim = self.embedding_provider.similarity(query_vec, c["embedding"])
            if sim >= min_similarity:
                c_copy = dict(c)
                c_copy["relevance_score"] = float(sim)
                vector_ranked.append(c_copy)
        vector_ranked.sort(key=lambda x: x["relevance_score"], reverse=True)

        # 2. Sparse BM25 Keyword Search
        bm25_scored = self.bm25_retriever.score_chunks(query, chunk_dicts)
        bm25_ranked = []
        for c, score in bm25_scored:
            if score > 0.0:
                c_copy = dict(c)
                c_copy["bm25_score"] = round(score, 4)
                bm25_ranked.append(c_copy)
        bm25_ranked.sort(key=lambda x: x.get("bm25_score", 0.0), reverse=True)

        # 3. Hybrid Reciprocal Rank Fusion (RRF)
        fused_results = reciprocal_rank_fusion(
            vector_results=vector_ranked,
            bm25_results=bm25_ranked,
            k=60,
            dense_weight=0.60
        )

        if fused_results:
            return fused_results[:top_k]

        # Fallback to vector results if fusion produced no matches
        return vector_ranked[:top_k]
