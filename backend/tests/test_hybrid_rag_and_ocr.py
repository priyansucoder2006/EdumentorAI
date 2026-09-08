import os
import pytest
import tempfile
from app.services.hybrid_retriever import BM25Retriever, reciprocal_rank_fusion
from app.services.vector_store import VectorStoreService
from app.services.document_ingestion import DocumentIngestionService
from app.models.document import Document, DocumentChunk


def test_bm25_retriever_scores_keywords():
    retriever = BM25Retriever()
    chunks = [
        {"id": "c1", "chunk_text": "Mitochondria is the powerhouse of the cell generating ATP energy."},
        {"id": "c2", "chunk_text": "Chloroplasts conduct photosynthesis in plant cells absorbing sunlight."},
        {"id": "c3", "chunk_text": "DNA replication occurs inside the nucleus during interphase."}
    ]

    scores = retriever.score_chunks("photosynthesis sunlight", chunks)
    scored_dict = {c["id"]: score for c, score in scores}
    assert scored_dict["c2"] > scored_dict["c1"]
    assert scored_dict["c2"] > scored_dict["c3"]


def test_reciprocal_rank_fusion():
    vector_res = [
        {"id": "101", "chunk_text": "First vector hit", "relevance_score": 0.95},
        {"id": "102", "chunk_text": "Second vector hit", "relevance_score": 0.85},
        {"id": "103", "chunk_text": "Third vector hit", "relevance_score": 0.70}
    ]
    bm25_res = [
        {"id": "103", "chunk_text": "Third vector hit is top keyword match", "bm25_score": 4.5},
        {"id": "101", "chunk_text": "First vector hit", "bm25_score": 3.2}
    ]

    fused = reciprocal_rank_fusion(vector_res, bm25_res, k=60, dense_weight=0.5)
    assert len(fused) == 3
    # IDs 101 and 103 appear in both dense and sparse, so they should rank highest
    top_ids = [f["id"] for f in fused[:2]]
    assert "101" in top_ids
    assert "103" in top_ids


def test_document_ingestion_legacy_doc_rejection(db_session, test_user):
    service = DocumentIngestionService(db_session)
    
    # Create fake legacy .doc binary file with OLE signature
    with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as f:
        f.write(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' + b'\x00' * 100)
        temp_path = f.name

    doc = Document(
        user_id=test_user.id,
        filename="legacy_file.doc",
        file_type="doc",
        storage_path=temp_path,
        processing_status="pending"
    )
    db_session.add(doc)
    db_session.commit()

    try:
        # Ingestion should catch the legacy binary and reject gracefully
        with pytest.raises(ValueError, match="Legacy Microsoft Word .doc binary format is not supported"):
            service._extract_pages(temp_path, "doc")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_document_ingestion_text_extraction(db_session, test_user):
    service = DocumentIngestionService(db_session)
    
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", encoding="utf-8", delete=False) as f:
        f.write("# Chapter 1: Quantum Mechanics\n\nWave-particle duality is the concept in quantum mechanics that every particle may be described as either a particle or a wave.\n\n# Chapter 2: Schrödinger Equation\n\nThe Schrödinger equation governs the wave function of a quantum-mechanical system.")
        temp_path = f.name

    try:
        pages = service._extract_pages(temp_path, "txt")
        assert len(pages) == 2
        assert "Quantum Mechanics" in pages[0][1]
        assert "Wave-particle duality" in pages[0][2]
        assert "Schrödinger Equation" in pages[1][1]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
