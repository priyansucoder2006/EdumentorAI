import io

def test_document_upload_and_rag(client, auth_headers):
    # Upload sample educational text
    file_content = b"# Chapter 1: Newton's Laws of Motion\n\nNewton's first law of motion states that an object at rest remains at rest unless acted upon by a net external force.\n\n# Chapter 2: Force and Acceleration\n\nThe second law establishes F = ma where force equals mass times acceleration."
    
    res = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("physics_notes.txt", io.BytesIO(file_content), "text/plain")},
        data={"language": "en"}
    )
    assert res.status_code == 200
    doc_data = res.json()
    assert doc_data["filename"] == "physics_notes.txt"
    doc_id = doc_data["id"]

    # Test RAG query
    rag_res = client.post(
        "/api/rag/query",
        headers=auth_headers,
        json={"query": "What is Newton's first law?", "document_id": doc_id}
    )
    assert rag_res.status_code == 200
    rag_data = rag_res.json()
    assert rag_data["is_grounded_in_docs"] is True
    assert len(rag_data["chunks"]) > 0
