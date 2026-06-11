from typing import Sequence
import numpy as np


class SimilarityEngine:
    @staticmethod
    def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
        va = np.array(a, dtype=float)
        vb = np.array(b, dtype=float)
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)

    def max_similarity(self, query_embedding: Sequence[float], corpus_embeddings: list[Sequence[float]]) -> float:
        if not corpus_embeddings:
            return 0.0
        return max(self.cosine_similarity(query_embedding, item) for item in corpus_embeddings)

    def classify(self, score: float, review_threshold: float, reject_threshold: float) -> str:
        if score >= reject_threshold:
            return "reject"
        if score >= review_threshold:
            return "review"
        return "approve"
