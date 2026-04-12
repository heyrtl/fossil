from __future__ import annotations
from typing import List, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError
import json

from .schema import FossilRecord


class RemoteStore:
    """
    Talks to a running FOSSIL REST API instead of local SQLite.
    Drop-in replacement for FossilStore.

    Usage:
        from fossil.remote import RemoteStore
        from fossil import Fossil

        store = RemoteStore("https://fossil-api.hello-76a.workers.dev")
        fossil = Fossil(store=store)
    """

    def __init__(self, api_url: str):
        self._base = api_url.rstrip("/")

    def _request(
        self,
        path: str,
        method: str = "GET",
        body: Optional[dict] = None,
    ) -> dict | list:
        url = f"{self._base}{path}"
        data = json.dumps(body).encode() if body is not None else None
        headers = {"User-Agent": "openfossil-sdk/0.1.2"}
        if data:
            headers["Content-Type"] = "application/json"
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            body_text = e.read().decode()
            raise RuntimeError(f"FOSSIL API {method} {path} → {e.code}: {body_text}") from e

    def insert(self, record: FossilRecord) -> FossilRecord:
        result = self._request("/records", method="POST", body=record.to_dict())
        return FossilRecord.from_dict(result)  # type: ignore[arg-type]

    def search(
        self,
        situation_text: str,
        top_k: int = 5,
        min_score: float = 0.5,
        domain: Optional[str] = None,
    ) -> List[Tuple[FossilRecord, float]]:
        params: dict = {"q": situation_text, "top_k": top_k, "min_score": min_score}
        if domain:
            params["domain"] = domain
        path = f"/search?{urlencode(params)}"
        results = self._request(path)
        return [
            (FossilRecord.from_dict(r["record"]), r["score"])  # type: ignore[index]
            for r in results  # type: ignore[union-attr]
        ]

    def get(self, fossil_id: str) -> Optional[FossilRecord]:
        try:
            result = self._request(f"/records/{fossil_id}")
            return FossilRecord.from_dict(result)  # type: ignore[arg-type]
        except RuntimeError as e:
            if "404" in str(e):
                return None
            raise

    def delete(self, fossil_id: str) -> bool:
        try:
            self._request(f"/records/{fossil_id}", method="DELETE")
            return True
        except RuntimeError as e:
            if "404" in str(e):
                return False
            raise

    def count(self) -> int:
        result = self._request("/records?limit=1")
        return result.get("total", 0)  # type: ignore[union-attr]

    def list_all(self, limit: int = 100, offset: int = 0) -> List[FossilRecord]:
        result = self._request(f"/records?{urlencode({'limit': limit, 'offset': offset})}")
        return [FossilRecord.from_dict(r) for r in result.get("items", [])]  # type: ignore[union-attr]

    def close(self) -> None:
        pass

    def __enter__(self) -> RemoteStore:
        return self

    def __exit__(self, *_) -> None:
        pass