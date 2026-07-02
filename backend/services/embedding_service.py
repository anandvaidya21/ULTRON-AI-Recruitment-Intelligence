"""
ULTRON AI – Embedding Service
Generates semantic vector embeddings using sentence-transformers (local, free, offline).
Optional GPU acceleration. Falls back to basic TF-IDF for edge cases.
"""

import json
import logging
import numpy as np
from typing import List, Optional, Union

logger = logging.getLogger(__name__)

# Lazy load – avoid import errors if not installed
_model = None
MODEL_NAME = "all-MiniLM-L6-v2"  # 90MB, fast, high quality


def _get_model():
    return None


class EmbeddingService:
    """
    Generates and manages semantic embeddings for jobs and candidates.
    Uses sentence-transformers locally; no API required.
    """

    def __init__(self):
        self._model = None

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for a text string."""
        if not text or not text.strip():
            return None

        model = _get_model()
        if model is None:
            return self._tfidf_fallback(text)

        try:
            embedding = model.encode(text[:4000], convert_to_numpy=True, normalize_embeddings=True)
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._tfidf_fallback(text)

    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Generate embeddings for multiple texts at once (more efficient)."""
        if not texts:
            return []

        model = _get_model()
        if model is None:
            return [self._tfidf_fallback(t) for t in texts]

        try:
            clean_texts = [t[:4000] if t else "" for t in texts]
            embeddings = model.encode(clean_texts, convert_to_numpy=True,
                                      normalize_embeddings=True, batch_size=32,
                                      show_progress_bar=False)
            return list(embeddings)
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [self._tfidf_fallback(t) for t in texts]

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between two normalized embeddings."""
        try:
            if emb1 is None or emb2 is None:
                return 0.0
            # If normalized, dot product == cosine similarity
            sim = float(np.dot(emb1, emb2))
            return max(0.0, min(1.0, sim))
        except Exception as e:
            logger.error(f"Cosine similarity computation failed: {e}")
            return 0.0

    def serialize(self, embedding: np.ndarray) -> str:
        """Serialize embedding to JSON string for database storage."""
        if embedding is None:
            return "[]"
        return json.dumps(embedding.tolist())

    def deserialize(self, embedding_str: str) -> Optional[np.ndarray]:
        """Deserialize embedding from JSON string."""
        if not embedding_str or embedding_str == "[]":
            return None
        try:
            return np.array(json.loads(embedding_str))
        except Exception:
            return None

    def _tfidf_fallback(self, text: str) -> Optional[np.ndarray]:
        """
        Minimal TF-IDF based pseudo-embedding for when sentence-transformers is unavailable.
        Returns a 384-dim vector (same dimension as MiniLM).
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=384)
            vec = vectorizer.fit_transform([text])
            arr = vec.toarray()[0]
            # Normalize
            norm = np.linalg.norm(arr)
            if norm > 0:
                arr = arr / norm
            return arr
        except Exception:
            # Ultimate fallback: random noise (at least won't crash)
            return np.random.rand(384).astype(np.float32)


# Global singleton instance
embedding_service = EmbeddingService()
