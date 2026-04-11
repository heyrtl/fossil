from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

from .schema import FossilRecord
from .embedder import BaseEmbedder, cosine_similarity, get_default_embedder


DEFAULT_DB_PATH = Path.home() / ".fossil" / "fossil.db"


class FossilStore:
    def __init__(
        self,
        db_path: Path | str = DEFAULT_DB_PATH,
        embedder: Optional[BaseEmbedder] = None,
    ):
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._embedder = embedder or get_default_embedder()
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS fossils (
                id TEXT PRIMARY KEY,
                protocol_version TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data JSON NOT NULL,
                embedding BLOB NOT NULL,
                shared INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_shared ON fossils(shared);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON fossils(timestamp);
        """)
        self._conn.commit()

    def insert(self, record: FossilRecord) -> FossilRecord:
        text = self._situation_text(record)
        embedding = self._embedder.embed(text)
        blob = np.array(embedding, dtype=np.float32).tobytes()

        self._conn.execute(
            """
            INSERT OR REPLACE INTO fossils
                (id, protocol_version, timestamp, data, embedding, shared)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.protocol_version,
                record.timestamp,
                json.dumps(record.to_dict()),
                blob,
                int(record.shared),
            ),
        )
        self._conn.commit()
        return record

    def search(
        self,
        situation_text: str,
        top_k: int = 5,
        min_score: float = 0.5,
        domain: Optional[str] = None,
    ) -> List[Tuple[FossilRecord, float]]:
        query_vec = np.array(
            self._embedder.embed(situation_text), dtype=np.float32
        )

        cur = self._conn.execute(
            "SELECT id, data, embedding FROM fossils"
        )
        rows = cur.fetchall()

        scored: List[Tuple[FossilRecord, float]] = []
        for row_id, data_json, blob in rows:
            record = FossilRecord.from_dict(json.loads(data_json))

            if domain and record.agent.task_domain.value != domain:
                continue

            stored_vec = np.frombuffer(blob, dtype=np.float32)
            score = float(np.dot(query_vec, stored_vec))

            if score >= min_score:
                scored.append((record, round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def get(self, fossil_id: str) -> Optional[FossilRecord]:
        cur = self._conn.execute(
            "SELECT data FROM fossils WHERE id = ?", (fossil_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return FossilRecord.from_dict(json.loads(row[0]))

    def delete(self, fossil_id: str) -> bool:
        cur = self._conn.execute(
            "DELETE FROM fossils WHERE id = ?", (fossil_id,)
        )
        self._conn.commit()
        return cur.rowcount > 0

    def count(self) -> int:
        cur = self._conn.execute("SELECT COUNT(*) FROM fossils")
        return cur.fetchone()[0]

    def list_all(self, limit: int = 100, offset: int = 0) -> List[FossilRecord]:
        cur = self._conn.execute(
            "SELECT data FROM fossils ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [FossilRecord.from_dict(json.loads(r[0])) for r in cur.fetchall()]

    def close(self) -> None:
        self._conn.close()

    def _situation_text(self, record: FossilRecord) -> str:
        parts = [record.situation.description, record.failure.description]
        if record.situation.context_snapshot:
            parts.append(record.situation.context_snapshot[:512])
        return " | ".join(parts)

    def __enter__(self) -> FossilStore:
        return self

    def __exit__(self, *_) -> None:
        self.close()