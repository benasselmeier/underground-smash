from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path
from typing import Dict


class OverlayStateBackend:
    """Shared overlay state with sqlite canonical storage and text-file mirroring."""

    def __init__(self, text_base_dir: str | Path, db_path: str | Path, mode: str | None = None):
        self.text_base_dir = Path(text_base_dir).resolve()
        self.db_path = Path(db_path).resolve()
        raw_mode = (mode or os.environ.get("STATE_BACKEND", "sqlite")).strip().lower()
        self.mode = raw_mode if raw_mode in {"sqlite", "textfiles"} else "sqlite"
        self._init_lock = threading.Lock()
        self._initialized = False

        self.text_base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS overlay_state (
                path TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        return conn

    def _ensure_initialized(self) -> None:
        if self.mode != "sqlite" or self._initialized:
            return

        with self._init_lock:
            if self._initialized:
                return

            with self._connect() as conn:
                count = conn.execute("SELECT COUNT(*) FROM overlay_state").fetchone()[0]
                if count == 0:
                    for file_path in sorted(self.text_base_dir.rglob("*")):
                        if not file_path.is_file():
                            continue
                        rel_path = file_path.relative_to(self.text_base_dir).as_posix()
                        value = file_path.read_text(encoding="utf-8", errors="ignore")
                        conn.execute(
                            """
                            INSERT INTO overlay_state(path, value, updated_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                            ON CONFLICT(path) DO UPDATE SET
                                value=excluded.value,
                                updated_at=CURRENT_TIMESTAMP
                            """,
                            (rel_path, value),
                        )
                conn.commit()
            self._initialized = True

    def _normalize_path(self, relative_path: str | Path) -> str:
        rel = Path(str(relative_path).replace("\\", "/"))
        full = (self.text_base_dir / rel).resolve()
        full.relative_to(self.text_base_dir)
        return full.relative_to(self.text_base_dir).as_posix()

    def _write_text_mirror(self, rel_path: str, value: str) -> None:
        full_path = self.text_base_dir / Path(rel_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(value, encoding="utf-8")

    def get(self, relative_path: str | Path) -> str:
        rel_path = self._normalize_path(relative_path)

        if self.mode == "textfiles":
            try:
                return (self.text_base_dir / rel_path).read_text(encoding="utf-8")
            except Exception:
                return ""

        self._ensure_initialized()
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM overlay_state WHERE path = ?", (rel_path,)).fetchone()
            if row is not None:
                return row[0]

        try:
            fallback_value = (self.text_base_dir / rel_path).read_text(encoding="utf-8")
        except Exception:
            fallback_value = ""

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO overlay_state(path, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(path) DO UPDATE SET
                    value=excluded.value,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (rel_path, fallback_value),
            )
            conn.commit()
        return fallback_value

    def set(self, relative_path: str | Path, value: str) -> None:
        rel_path = self._normalize_path(relative_path)
        safe_value = "" if value is None else str(value)

        if self.mode == "textfiles":
            self._write_text_mirror(rel_path, safe_value)
            return

        self._ensure_initialized()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO overlay_state(path, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(path) DO UPDATE SET
                    value=excluded.value,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (rel_path, safe_value),
            )
            conn.commit()
        self._write_text_mirror(rel_path, safe_value)

    def bulk_set(self, values: Dict[str, str]) -> None:
        if self.mode == "textfiles":
            for rel_path, value in values.items():
                self.set(rel_path, value)
            return

        self._ensure_initialized()
        normalized = []
        for rel_path, value in values.items():
            normalized.append((self._normalize_path(rel_path), "" if value is None else str(value)))

        with self._connect() as conn:
            for rel_path, safe_value in normalized:
                conn.execute(
                    """
                    INSERT INTO overlay_state(path, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(path) DO UPDATE SET
                        value=excluded.value,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (rel_path, safe_value),
                )
            conn.commit()

        for rel_path, safe_value in normalized:
            self._write_text_mirror(rel_path, safe_value)

    def read_directory(self, relative_directory: str | Path) -> Dict[str, str]:
        rel_dir = str(relative_directory).strip().strip("/")
        target_dir = self.text_base_dir / rel_dir if rel_dir else self.text_base_dir
        if not target_dir.exists():
            return {}

        result: Dict[str, str] = {}
        for file_path in sorted(target_dir.iterdir()):
            if not file_path.is_file():
                continue
            rel_file = file_path.relative_to(self.text_base_dir).as_posix()
            result[file_path.name] = self.get(rel_file)
        return result
