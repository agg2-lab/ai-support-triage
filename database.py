import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "support.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                plan TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                needs_human INTEGER NOT NULL DEFAULT 0,
                suggested_article TEXT,
                draft_response TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL UNIQUE,
                helpful INTEGER NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ticket_id) REFERENCES tickets(id)
            )
            """
        )


def ticket_count():
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM tickets").fetchone()
    return row["count"]


def seed_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    with get_connection() as conn:
        for _, row in df.iterrows():
            conn.execute(
                """
                INSERT INTO tickets
                (subject, description, plan, category, priority, status, needs_human)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["subject"],
                    row["description"],
                    row["plan"],
                    row["category"],
                    row["priority"],
                    row["status"],
                    int(row["needs_human"]),
                ),
            )


def add_ticket(ticket):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets
            (
                subject,
                description,
                plan,
                category,
                priority,
                status,
                needs_human,
                suggested_article,
                draft_response
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket["subject"],
                ticket["description"],
                ticket["plan"],
                ticket["category"],
                ticket["priority"],
                "Open",
                int(ticket["needs_human"]),
                ticket.get("suggested_article"),
                ticket.get("draft_response"),
            ),
        )
        return cursor.lastrowid


def add_feedback(ticket_id: int, helpful: bool, notes: str = ""):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO feedback (ticket_id, helpful, notes)
            VALUES (?, ?, ?)
            ON CONFLICT(ticket_id) DO UPDATE SET
                helpful = excluded.helpful,
                notes = excluded.notes,
                created_at = CURRENT_TIMESTAMP
            """,
            (ticket_id, int(helpful), notes.strip()),
        )


def load_tickets():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT *
            FROM tickets
            ORDER BY datetime(created_at) DESC, id DESC
            """,
            conn,
        )


def load_feedback():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT
                feedback.id,
                feedback.ticket_id,
                feedback.helpful,
                feedback.notes,
                feedback.created_at,
                tickets.subject,
                tickets.category
            FROM feedback
            JOIN tickets ON tickets.id = feedback.ticket_id
            ORDER BY datetime(feedback.created_at) DESC, feedback.id DESC
            """,
            conn,
        )
