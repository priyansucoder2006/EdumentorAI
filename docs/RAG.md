# RAG.md — Retrieval-Augmented Generation Architecture

## 1. Document Ingestion & Hierarchical Chunking Pipeline

```
UPLOAD DOCUMENT (PDF/DOCX/PPTX/TXT)
  ↓
FILE TYPE VALIDATION & SECURITY SCAN
  ↓
STRUCTURE DETECTION (Headings, Paragraphs, Slides, Pages)
  ↓
HIERARCHICAL CHUNKING (300-400 words with 50-word overlap)
  ↓
DENSE VECTOR EMBEDDING (384-dim BAAI/bge-m3 compatible)
  ↓
VECTOR DATABASE INDEXING (pgvector / Cosine Similarity Engine)
  ↓
INDEX READY
```

---

## 2. Hybrid Retrieval Engine

When a student queries or launches a lesson from uploaded material:
1. **Dense Semantic Search**: Computes cosine similarity between query embedding and all indexed chunk vectors.
2. **Metadata Filtering**: Scopes retrieval by `document_id`, `language`, and chapter sections.
3. **Threshold Filtering**: Chunks with cosine similarity score $< 0.15$ are discarded to prevent irrelevant noise.
4. **Top-K Reranking**: The top 4 most relevant chunks with page number and section citations are retrieved.

---

## 3. Grounding & Anti-Hallucination Policy

The RAG Agent classifies context into:
- **`uploaded_document`**: Content directly grounded in student documents. Citations with exact page numbers and section titles are supplied.
- **`general_knowledge`**: Used when no uploaded document matches. The AI explicitly alerts the learner:
  *"I couldn't find this information in your uploaded material. I am explaining this using general domain knowledge."*

---

## 4. Prompt Injection & Sandbox Security

Uploaded documents are treated strictly as passive **data/knowledge** and never executable instructions:
- Chunks are enclosed in explicit data brackets: `[Document Context: ...]`.
- System prompts enforce that instructions inside documents cannot override teacher behavior or bypass pedagogical constraints.
