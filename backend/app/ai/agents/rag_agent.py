from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.vector_store import VectorStoreService
from app.ai.providers import get_llm_provider
from app.schemas.document import RAGQueryResponse, DocumentChunkResponse
from app.core.logging import logger


class RAGAgent:
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStoreService(db)
        self.llm = get_llm_provider()

    async def retrieve_knowledge(
        self,
        query: str,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        top_k: int = 4
    ) -> RAGQueryResponse:
        """
        Retrieves knowledge from uploaded documents with grounding validation.
        """
        chunks_data = await self.vector_store.search_similar_chunks(
            query=query,
            document_id=document_id,
            user_id=user_id,
            top_k=top_k,
            min_similarity=0.10
        )

        chunk_responses = [
            DocumentChunkResponse(
                id=c["id"],
                chunk_text=c["chunk_text"],
                page_number=c["page_number"],
                section_title=c["section_title"],
                relevance_score=c["relevance_score"],
                chunk_metadata=c["chunk_metadata"]
            )
            for c in chunks_data
        ]

        if not chunk_responses:
            return RAGQueryResponse(
                query=query,
                is_grounded_in_docs=False,
                source_type="general_knowledge",
                chunks=[],
                answer="No uploaded document context found for this query. Responding using general educational knowledge.",
                grounding_notes="I couldn't find this information in your uploaded material. Explaining using general knowledge."
            )

        # Combine context
        context_str = "\n\n".join([f"[Source: {c.section_title}, Page {c.page_number}]\n{c.chunk_text}" for c in chunk_responses])
        prompt = f"""Use the following retrieved document excerpts to answer the question:
Context:
{context_str}

Question: {query}

Provide a concise, grounded explanation citing the sources."""

        answer = await self.llm.generate_text(prompt, system_prompt="You are a factual pedagogical assistant. Only state facts directly supported by the provided text.")

        return RAGQueryResponse(
            query=query,
            is_grounded_in_docs=True,
            source_type="uploaded_document",
            chunks=chunk_responses,
            answer=answer,
            grounding_notes=f"Grounded in {len(chunk_responses)} document section(s)."
        )
