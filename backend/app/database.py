import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.seed_data import INITIAL_COLUMNS, INITIAL_CARDS

DEFAULT_DATABASE_PATH = Path("/app/data/kanban.sqlite3")
USER_ID = "user-1"
BOARD_ID = "board-user-1"


def database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS boards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS columns (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(board_id, position)
            );
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(board_id, id)
            );
            CREATE TABLE IF NOT EXISTS board_cards (
                card_id TEXT PRIMARY KEY REFERENCES cards(id) ON DELETE CASCADE,
                column_id TEXT NOT NULL REFERENCES columns(id) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(column_id, position)
            );
            """
        )
        now = utc_now()
        connection.execute(
            "INSERT OR IGNORE INTO users (id, username, created_at) VALUES (?, ?, ?)",
            (USER_ID, "user", now),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO boards (id, user_id, name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (BOARD_ID, USER_ID, "Kanban Studio", now, now),
        )
        for position, (column_id, title, _) in enumerate(INITIAL_COLUMNS):
            connection.execute(
                """
                INSERT OR IGNORE INTO columns
                    (id, board_id, title, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (column_id, BOARD_ID, title, position, now, now),
            )
        for column_id, _, card_ids in INITIAL_COLUMNS:
            for position, card_id in enumerate(card_ids):
                card = INITIAL_CARDS[card_id]
                connection.execute(
                    """
                    INSERT OR IGNORE INTO cards
                        (id, board_id, title, details, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (card_id, BOARD_ID, card["title"], card["details"], now, now),
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO board_cards
                        (card_id, column_id, position, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (card_id, column_id, position, now),
                )


def get_board(username: str) -> dict | None:
    with connect() as connection:
        board = connection.execute(
            """
            SELECT boards.id, boards.name
            FROM boards JOIN users ON users.id = boards.user_id
            WHERE users.username = ?
            """,
            (username,),
        ).fetchone()
        if board is None:
            return None
        columns = connection.execute(
            "SELECT id, title FROM columns WHERE board_id = ? ORDER BY position",
            (board["id"],),
        ).fetchall()
        cards = connection.execute(
            """
            SELECT cards.id, cards.title, cards.details, board_cards.column_id
            FROM cards JOIN board_cards ON board_cards.card_id = cards.id
            WHERE cards.board_id = ?
            ORDER BY board_cards.column_id, board_cards.position
            """,
            (board["id"],),
        ).fetchall()
        card_lookup = {
            row["id"]: {"id": row["id"], "title": row["title"], "details": row["details"]}
            for row in cards
        }
        card_ids_by_column = {row["id"]: [] for row in columns}
        for row in cards:
            card_ids_by_column[row["column_id"]].append(row["id"])
        return {
            "id": board["id"],
            "name": board["name"],
            "columns": [
                {"id": row["id"], "title": row["title"], "cardIds": card_ids_by_column[row["id"]]}
                for row in columns
            ],
            "cards": card_lookup,
        }


def board_id_for_user(connection: sqlite3.Connection, username: str) -> str | None:
    row = connection.execute(
        "SELECT boards.id FROM boards JOIN users ON users.id = boards.user_id WHERE users.username = ?",
        (username,),
    ).fetchone()
    return row["id"] if row else None


def rename_column(username: str, column_id: str, title: str) -> bool:
    with connect() as connection:
        board_id = board_id_for_user(connection, username)
        result = connection.execute(
            "UPDATE columns SET title = ?, updated_at = ? WHERE id = ? AND board_id = ?",
            (title, utc_now(), column_id, board_id),
        )
        if result.rowcount == 0:
            return False
        connection.execute("UPDATE boards SET updated_at = ? WHERE id = ?", (utc_now(), board_id))
        return True


def create_card(username: str, card_id: str, title: str, details: str, column_id: str) -> bool:
    with connect() as connection:
        board_id = board_id_for_user(connection, username)
        column = connection.execute(
            "SELECT id FROM columns WHERE id = ? AND board_id = ?", (column_id, board_id)
        ).fetchone()
        if column is None:
            return False
        position_row = connection.execute(
            "SELECT COALESCE(MAX(position) + 1, 0) AS position FROM board_cards WHERE column_id = ?",
            (column_id,),
        ).fetchone()
        now = utc_now()
        connection.execute(
            "INSERT INTO cards (id, board_id, title, details, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (card_id, board_id, title, details, now, now),
        )
        connection.execute(
            "INSERT INTO board_cards (card_id, column_id, position, updated_at) VALUES (?, ?, ?, ?)",
            (card_id, column_id, position_row["position"], now),
        )
        connection.execute("UPDATE boards SET updated_at = ? WHERE id = ?", (now, board_id))
        return True


def update_card(username: str, card_id: str, title: str, details: str) -> bool:
    with connect() as connection:
        board_id = board_id_for_user(connection, username)
        result = connection.execute(
            "UPDATE cards SET title = ?, details = ?, updated_at = ? WHERE id = ? AND board_id = ?",
            (title, details, utc_now(), card_id, board_id),
        )
        return result.rowcount > 0


def delete_card(username: str, card_id: str) -> bool:
    with connect() as connection:
        board_id = board_id_for_user(connection, username)
        result = connection.execute("DELETE FROM cards WHERE id = ? AND board_id = ?", (card_id, board_id))
        return result.rowcount > 0


def move_card(username: str, card_id: str, column_id: str, position: int) -> bool:
    with connect() as connection:
        board_id = board_id_for_user(connection, username)
        membership = connection.execute(
            """
            SELECT board_cards.column_id, board_cards.position
            FROM board_cards JOIN cards ON cards.id = board_cards.card_id
            WHERE board_cards.card_id = ? AND cards.board_id = ?
            """,
            (card_id, board_id),
        ).fetchone()
        target = connection.execute(
            "SELECT id FROM columns WHERE id = ? AND board_id = ?", (column_id, board_id)
        ).fetchone()
        if membership is None or target is None or position < 0:
            return False
        source_column_id = membership["column_id"]
        source_ids = [
            row["card_id"] for row in connection.execute(
                "SELECT card_id FROM board_cards WHERE column_id = ? ORDER BY position", (source_column_id,)
            )
        ]
        target_ids = source_ids if source_column_id == column_id else [
            row["card_id"] for row in connection.execute(
                "SELECT card_id FROM board_cards WHERE column_id = ? ORDER BY position", (column_id,)
            )
        ]
        source_ids.remove(card_id)
        if source_column_id == column_id:
            ordered_ids = source_ids
        else:
            ordered_ids = target_ids
        insert_at = min(position, len(ordered_ids))
        ordered_ids.insert(insert_at, card_id)
        now = utc_now()
        connection.execute("UPDATE board_cards SET position = position + 1000000 WHERE column_id IN (?, ?)", (source_column_id, column_id))
        for index, ordered_card_id in enumerate(source_ids if source_column_id != column_id else ordered_ids):
            connection.execute(
                "UPDATE board_cards SET position = ?, updated_at = ? WHERE card_id = ?",
                (index, now, ordered_card_id),
            )
        if source_column_id != column_id:
            for index, ordered_card_id in enumerate(ordered_ids):
                connection.execute(
                    "UPDATE board_cards SET column_id = ?, position = ?, updated_at = ? WHERE card_id = ?",
                    (column_id, index, now, ordered_card_id),
                )
        connection.execute("UPDATE boards SET updated_at = ? WHERE id = ?", (now, board_id))
        return True
