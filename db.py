import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import config
from prompts import PERSPECTIVES

# One TEXT column per answer, derived from PERSPECTIVES so they cannot drift.
ANSWER_COLUMNS = ["key_facts"] + [p.key for p in PERSPECTIVES]
# v2: one response column per perspective.
V2_COLUMNS = [f"{p.key}_v2" for p in PERSPECTIVES]


def _create_table(conn: sqlite3.Connection) -> None:
    answer_cols = ",\n    ".join(f"{c} TEXT" for c in ANSWER_COLUMNS)
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            model TEXT NOT NULL,
            situation TEXT NOT NULL,
            {answer_cols},
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost_usd REAL
        )
        """
    )


def _migrate_old_answers(conn: sqlite3.Connection) -> None:
    """Old rows kept all answers as JSON in one `answers` column. Split them into columns."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(requests)")}
    if "answers" not in existing:
        return
    for col in ANSWER_COLUMNS:
        if col not in existing:
            conn.execute(f"ALTER TABLE requests ADD COLUMN {col} TEXT")
    for row_id, raw in conn.execute("SELECT id, answers FROM requests").fetchall():
        data = json.loads(raw)
        values = [data.get("key_facts")] + [
            (data.get(p.key) or {}).get("response") for p in PERSPECTIVES
        ]
        sets = ", ".join(f"{c} = ?" for c in ANSWER_COLUMNS)
        conn.execute(f"UPDATE requests SET {sets} WHERE id = ?", (*values, row_id))
    conn.execute("ALTER TABLE requests DROP COLUMN answers")


def _add_v2_columns(conn: sqlite3.Connection) -> None:
    """Add the v2 columns. Moves any earlier JSON `answers_v2` into them, then drops it."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(requests)")}
    for col in V2_COLUMNS:
        if col not in existing:
            conn.execute(f"ALTER TABLE requests ADD COLUMN {col} TEXT")
    if "answers_v2" in existing:
        for row_id, raw in conn.execute(
            "SELECT id, answers_v2 FROM requests WHERE answers_v2 IS NOT NULL"
        ).fetchall():
            old = json.loads(raw)
            _update_v2(
                conn,
                row_id,
                {k: v["response"] if isinstance(v, dict) else v for k, v in old.items()},
            )
        conn.execute("ALTER TABLE requests DROP COLUMN answers_v2")


def _update_v2(conn: sqlite3.Connection, request_id: int, answers: dict[str, str]) -> None:
    values = [answers[p.key] for p in PERSPECTIVES]
    sets = ", ".join(f"{c} = ?" for c in V2_COLUMNS)
    conn.execute(f"UPDATE requests SET {sets} WHERE id = ?", (*values, request_id))


@contextmanager
def _connect():
    """Open the database, make sure the table is current, commit on success."""
    path = Path(config.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        with conn:  # one transaction: commits on success, rolls back on error
            _create_table(conn)
            _migrate_old_answers(conn)
            _add_v2_columns(conn)
            yield conn
    finally:
        conn.close()


def save_request(
    situation: str,
    answers: dict[str, str] | None,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    cost_usd: float | None,
) -> int:
    """Store one request. `answers` maps each ANSWER_COLUMNS name to its text.

    answers is None for a fallback request (not a personal issue): the answer columns stay
    NULL, and a row with no `willingness` is how a fallback is recognised.
    cost_usd is None when the model has no price data.
    """
    cols = ["created_at", "model", "situation", *ANSWER_COLUMNS,
            "input_tokens", "output_tokens", "cost_usd"]
    with _connect() as conn:
        cur = conn.execute(
            f"INSERT INTO requests ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
            (
                datetime.now(timezone.utc).isoformat(),
                model,
                situation,
                *((answers[c] if answers else None) for c in ANSWER_COLUMNS),
                input_tokens,
                output_tokens,
                cost_usd,
            ),
        )
        return cur.lastrowid


def save_v2(request_id: int, answers_v2: dict[str, str]) -> None:
    """Attach v2 answers ({perspective: text}) to a saved request."""
    with _connect() as conn:
        _update_v2(conn, request_id, answers_v2)


def v2_answers(row: dict) -> dict[str, str] | None:
    """The v2 answers of a saved row as {perspective: text}, or None if it has none."""
    if row.get(V2_COLUMNS[0]) is None:
        return None
    return {p.key: row[f"{p.key}_v2"] for p in PERSPECTIVES}


def list_requests() -> list[dict]:
    """All saved requests, newest first: id, created_at, situation, cost_usd, is_fallback."""
    if not Path(config.DB_PATH).exists():
        return []
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, created_at, situation, cost_usd,"
            " (willingness IS NULL AND willingness_v2 IS NULL) AS is_fallback"
            " FROM requests ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def format_when(created_at: str) -> str:
    """Stored UTC ISO string -> 'YYYY-MM-DD HH:MM IST'."""
    dt = datetime.fromisoformat(created_at).astimezone(config.DISPLAY_TZ)
    return f"{dt:%Y-%m-%d %H:%M} {config.DISPLAY_TZ_LABEL}"


def get_request(request_id: int) -> dict | None:
    """One saved request with every column, or None if it does not exist."""
    if not Path(config.DB_PATH).exists():
        return None
    with _connect() as conn:
        row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    return dict(row) if row else None
