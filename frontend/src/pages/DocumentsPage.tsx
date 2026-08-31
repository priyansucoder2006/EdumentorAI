import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentService } from '../services/documentService';
import { DocumentItem } from '../types';
import {
  UploadCloud,
  FileText,
  Trash2,
  BookOpen,
  Search,
  CheckCircle,
  Clock,
  Sparkles,
  AlertCircle,
} from 'lucide-react';

export const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [ragQuery, setRagQuery] = useState<string>('');
  const [ragResult, setRagResult] = useState<any>(null);
  const [isSearchingRag, setIsSearchingRag] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchDocs = async () => {
    try {
      const docs = await documentService.getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.warn('Error fetching docs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setUploading(true);

    try {
      await documentService.uploadDocument(files[0]);
      setTimeout(fetchDocs, 1000);
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentService.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;
    setIsSearchingRag(true);

    try {
      const res = await documentService.queryRAG(ragQuery);
      setRagResult(res);
    } catch (err) {
      console.error('RAG search error:', err);
    } finally {
      setIsSearchingRag(false);
    }
  };

  return (
    <div className="documents-page-container">
      <div className="page-header">
        <div>
          <h2>Document Intelligence & RAG Grounding Hub</h2>
          <p>Upload textbooks, class notes, and research papers for grounded AI teaching and citations.</p>
        </div>
      </div>

      <div className="documents-grid-layout">
        {/* Upload & List Column */}
        <div className="doc-col-left">
          {/* Upload Dropzone */}
          <div className="upload-dropzone-card">
            <UploadCloud size={40} className="text-blue-400 mb-2" />
            <h3>Upload Educational Documents</h3>
            <p>Supports PDF, DOCX, PPTX, TXT, Scanned Notes (Max 25 MB)</p>
            <label className="btn-primary mt-3 cursor-pointer">
              <span>{uploading ? 'Processing & Indexing Vector Chunks...' : 'Choose File to Upload'}</span>
              <input
                type="file"
                className="hidden"
                accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md"
                onChange={handleFileUpload}
                disabled={uploading}
              />
            </label>
          </div>

          {/* Uploaded Documents List */}
          <div className="documents-list-section">
            <h3 className="section-title">Indexed Documents ({documents.length})</h3>
            {documents.length === 0 ? (
              <div className="empty-state-box">
                <FileText size={32} className="text-slate-500 mb-2" />
                <p>No documents uploaded yet. Upload your first syllabus notes!</p>
              </div>
            ) : (
              <div className="docs-cards-stack">
                {documents.map((doc) => (
                  <div key={doc.id} className="doc-item-row">
                    <div className="doc-icon-col">
                      <FileText size={22} className="text-blue-400" />
                    </div>
                    <div className="doc-meta-col">
                      <span className="doc-filename">{doc.filename}</span>
                      <div className="doc-submeta">
                        <span className="doc-type-badge">{doc.file_type.toUpperCase()}</span>
                        <span>{doc.page_count} pages</span>
                        <span className="status-badge indexed flex items-center gap-1">
                          <CheckCircle size={12} /> {doc.processing_status}
                        </span>
                      </div>
                    </div>
                    <div className="doc-actions-col">
                      <button
                        className="btn-primary btn-sm"
                        onClick={() =>
                          navigate('/create-lesson', {
                            state: { document_id: doc.id, topic: doc.filename.split('.')[0] },
                          })
                        }
                      >
                        <BookOpen size={14} /> Teach
                      </button>
                      <button
                        className="btn-icon-danger"
                        onClick={() => handleDelete(doc.id)}
                        title="Delete Document"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RAG Retrieval Explorer Column */}
        <div className="doc-col-right">
          <div className="rag-playground-card">
            <div className="flex items-center gap-2 mb-2 font-bold text-blue-400">
              <Search size={18} />
              <span>RAG Knowledge Retrieval Explorer</span>
            </div>
            <p className="text-xs text-slate-300 mb-3">
              Test semantic hybrid retrieval across all your indexed notes and inspect chunk relevance scores.
            </p>

            <form onSubmit={handleRagSearch} className="rag-search-form">
              <input
                type="text"
                placeholder="Ask any question from your documents..."
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
              />
              <button type="submit" className="btn-primary btn-sm" disabled={isSearchingRag}>
                {isSearchingRag ? 'Retrieving...' : 'Retrieve Context'}
              </button>
            </form>

            {ragResult && (
              <div className="rag-results-box animate-fade-in mt-4">
                <div className="grounding-status-pill">
                  <Sparkles size={14} className="text-blue-400" />
                  <span>Grounding: {ragResult.source_type}</span>
                </div>

                <div className="rag-answer-box">
                  <h5>Synthesized Answer:</h5>
                  <p>{ragResult.answer}</p>
                </div>

                {ragResult.chunks && ragResult.chunks.length > 0 && (
                  <div className="retrieved-chunks-list">
                    <h6>Retrieved Citations ({ragResult.chunks.length} chunks):</h6>
                    {ragResult.chunks.map((chunk: any, i: number) => (
                      <div key={i} className="chunk-citation-card">
                        <div className="chunk-header">
                          <span>Page {chunk.page_number} — {chunk.section_title}</span>
                          <span className="relevance-score">
                            Score: {(chunk.relevance_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <p className="chunk-snippet">{chunk.chunk_text}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
