import math
import re
from typing import List, Dict, Any, Tuple
from collections import Counter


class BM25Retriever:
    """
    In-memory BM25 (Best Matching 25) sparse keyword retrieval engine
    for document chunks.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def tokenize(self, text: str) -> List[str]:
        # Lowercase and extract alphanumeric words
        return re.findall(r'\b[a-z0-9_]+\b', text.lower())

    def score_chunks(self, query: str, chunks: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
        query_tokens = self.tokenize(query)
        if not query_tokens or not chunks:
            return [(c, 0.0) for c in chunks]

        # 1. Corpus Statistics
        N = len(chunks)
        doc_tokens_list = [self.tokenize(c.get("chunk_text", "")) for c in chunks]
        doc_lens = [len(dt) for dt in doc_tokens_list]
        avgdl = sum(doc_lens) / float(N) if N > 0 else 1.0

        # 2. Document Frequency per query term
        df = Counter()
        for dt in doc_tokens_list:
            unique_terms = set(dt)
            for qt in query_tokens:
                if qt in unique_terms:
                    df[qt] += 1

        # 3. Calculate BM25 score for each chunk
        scored = []
        for idx, chunk in enumerate(chunks):
            dt = doc_tokens_list[idx]
            dt_len = doc_lens[idx]
            dt_counts = Counter(dt)

            score = 0.0
            for qt in query_tokens:
                if qt not in dt_counts:
                    continue
                tf = dt_counts[qt]
                doc_freq = df[qt]
                # Standard Lucene/BM25 IDF formula
                idf = math.log(1.0 + (N - doc_freq + 0.5) / (doc_freq + 0.5))
                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dt_len / max(1.0, avgdl)))
                score += idf * (num / max(0.001, denom))

            scored.append((chunk, max(0.0, score)))

        return scored


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = 60,
    dense_weight: float = 0.55
) -> List[Dict[str, Any]]:
    """
    Combines dense semantic vector rankings with sparse BM25 keyword rankings
    using Reciprocal Rank Fusion (RRF).
    """
    fused_scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}
    sources_map: Dict[str, Dict[str, Any]] = {}

    # Rank dense vector results
    for rank, item in enumerate(vector_results):
        cid = str(item["id"])
        chunk_map[cid] = item
        score = dense_weight * (1.0 / (k + rank + 1))
        fused_scores[cid] = fused_scores.get(cid, 0.0) + score
        sources_map[cid] = {
            "vector_rank": rank + 1,
            "vector_score": item.get("relevance_score", 0.0),
            "bm25_rank": None
        }

    # Rank BM25 results
    for rank, item in enumerate(bm25_results):
        cid = str(item["id"])
        chunk_map[cid] = item
        score = (1.0 - dense_weight) * (1.0 / (k + rank + 1))
        fused_scores[cid] = fused_scores.get(cid, 0.0) + score
        if cid not in sources_map:
            sources_map[cid] = {
                "vector_rank": None,
                "vector_score": 0.0,
                "bm25_rank": rank + 1
            }
        else:
            sources_map[cid]["bm25_rank"] = rank + 1

    # Sort combined results descending by fused score
    sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

    final_results = []
    for cid in sorted_ids:
        chunk = dict(chunk_map[cid])
        meta = chunk.get("chunk_metadata", {}) or {}
        meta["retrieval_fusion"] = sources_map[cid]
        meta["hybrid_rrf_score"] = round(fused_scores[cid], 5)
        chunk["chunk_metadata"] = meta
        chunk["relevance_score"] = round(fused_scores[cid] * 100.0, 2)
        final_results.append(chunk)

    return final_results
