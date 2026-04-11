from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        ...

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class LocalEmbedder(BaseEmbedder):
    """
    Runs entirely on-device via sentence-transformers.
    No API key. No data leaves the machine.
    Model is downloaded once and cached by HuggingFace.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embedding. "
                "Install it with: pip install sentence-transformers"
            )
        self._model = SentenceTransformer(model_name)
        self._dim = self._model.get_embedding_dimension()

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> List[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()


class OpenAIEmbedder(BaseEmbedder):
    """
    Drop-in for users who want OpenAI embeddings.
    Requires: pip install openai
    """

    def __init__(self, model_name: str, api_key: str):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        self._client = OpenAI(api_key=api_key)
        self._model_name = model_name

    def embed(self, text: str) -> List[float]:
        resp = self._client.embeddings.create(input=text, model=self._model_name)
        return resp.data[0].embedding


def cosine_similarity(a: List[float], b: List[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def get_default_embedder() -> LocalEmbedder:
    return LocalEmbedder()