from __future__ import annotations

import logging
from typing import List, Any

logger = logging.getLogger("justor.reranker")

try:
    from flashrank import Ranker, RerankRequest
    FLASHRANK_AVAILABLE = True
except ImportError:
    FLASHRANK_AVAILABLE = False
    logger.warning("flashrank is not installed; LegalReranker will use fallback scoring.")


class LegalReranker:
    """
    Cross-encoder reranker for legal provisions.
    Computes fine-grained semantic interaction between user query and retrieved sections
    to elevate the exact controlling statutory section (e.g. s.53A vs s.53) to Rank 1.
    """

    _instance = None

    def __init__(self, model_name: str = "ms-marco-TinyBERT-L-2-v2"):
        self.ranker = None
        if FLASHRANK_AVAILABLE:
            try:
                # Initialize lightweight in-memory cross-encoder (~3.2MB onnx model)
                self.ranker = Ranker(model_name=model_name, cache_dir=".cache/flashrank")
                logger.info("LegalReranker initialized with model: %s", model_name)
            except Exception as e:
                logger.warning("Failed to initialize FlashRank: %s. Falling back to passthrough.", e)

    @classmethod
    def get_instance(cls) -> "LegalReranker":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def rerank_evidence(self, query: str, items: List[Any], top_k: int = 6) -> List[Any]:
        """
        Reranks a list of EvidenceItem objects based on cross-encoder relevance to query.
        Returns reordered list with updated relevance scores.
        """
        if not items or len(items) <= 1:
            return items

        if not self.ranker:
            return items[:top_k]

        try:
            passages = []
            for idx, item in enumerate(items):
                act_name = getattr(item, "act_name", "") or ""
                sec_num = getattr(item, "section_number", "") or ""
                heading = getattr(item, "heading", "") or ""
                legal_text = getattr(item, "legal_text", "") or ""
                
                # Combine metadata and text for precise statutory matching
                content = f"{act_name} Section {sec_num}: {heading}\n{legal_text[:800]}"
                passages.append({
                    "id": idx,
                    "text": content
                })

            req = RerankRequest(query=query, passages=passages)
            results = self.ranker.rerank(req)

            # Map results back to original EvidenceItem objects
            reranked_items = []
            for r in results:
                orig_idx = r["id"]
                score = r.get("score", 0.0)
                item = items[orig_idx]
                item.rerank_score = float(score)
                reranked_items.append((score, item))

            # Filter out extreme noise if we have high-confidence matches
            best_score = reranked_items[0][0] if reranked_items else 0.0
            filtered = []
            for score, it in reranked_items:
                if best_score > 0.7 and score < 0.05 and len(filtered) >= 2:
                    continue
                filtered.append(it)

            return filtered[:top_k]

        except Exception as e:
            logger.warning("Reranking failed (%s); preserving original order.", e)
            return items[:top_k]


# Global instance
legal_reranker = LegalReranker.get_instance()
