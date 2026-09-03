import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture
def board_client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "kanban.sqlite3"))
    database.initialize_database()
    with TestClient(app) as client:
        yield client


def auth_headers() -> dict[str, str]:
    return {"X-Username": "user"}


def test_requires_matching_user_header(board_client: TestClient) -> None:
    assert board_client.get("/api/boards/user").status_code == 401
    assert board_client.get("/api/boards/user", headers={"X-Username": "other"}).status_code == 401
    assert board_client.get(
        "/api/boards/unknown", headers={"X-Username": "unknown"}
    ).status_code == 404


def test_reads_seeded_board(board_client: TestClient) -> None:
    response = board_client.get("/api/boards/user", headers=auth_headers())

    assert response.status_code == 200
    board = response.json()
    assert len(board["columns"]) == 5
    assert board["columns"][0]["cardIds"] == ["card-1", "card-2"]
    assert board["cards"]["card-1"]["title"] == "Align roadmap themes"


def test_renames_column_and_edits_card(board_client: TestClient) -> None:
    rename = board_client.patch(
        "/api/boards/user/columns/col-backlog",
        headers=auth_headers(),
        json={"title": "Ideas"},
    )
    edit = board_client.patch(
        "/api/boards/user/cards/card-1",
        headers=auth_headers(),
        json={"title": "Updated roadmap", "details": "New details"},
    )

    assert rename.status_code == 200
    assert rename.json()["columns"][0]["title"] == "Ideas"
    assert edit.status_code == 200
    assert edit.json()["cards"]["card-1"] == {
        "id": "card-1",
        "title": "Updated roadmap",
        "details": "New details",
    }


def test_creates_moves_and_deletes_card(board_client: TestClient) -> None:
    created = board_client.post(
        "/api/boards/user/cards",
        headers=auth_headers(),
        json={
            "id": "card-new",
            "title": "New card",
            "details": "Notes",
            "column_id": "col-backlog",
        },
    )
    moved = board_client.post(
        "/api/boards/user/cards/card-new/move",
        headers=auth_headers(),
        json={"column_id": "col-review", "position": 0},
    )
    deleted = board_client.delete(
        "/api/boards/user/cards/card-new", headers=auth_headers()
    )

    assert created.status_code == 201
    assert created.json()["columns"][0]["cardIds"] == ["card-1", "card-2", "card-new"]
    assert moved.status_code == 200
    moved_board = moved.json()
    assert moved_board["columns"][3]["cardIds"] == ["card-new", "card-6"]
    assert moved_board["columns"][0]["cardIds"] == ["card-1", "card-2"]
    assert deleted.status_code == 200
    assert "card-new" not in deleted.json()["cards"]


def test_rejects_invalid_mutations(board_client: TestClient) -> None:
    missing_column = board_client.post(
        "/api/boards/user/cards",
        headers=auth_headers(),
        json={"id": "bad-card", "title": "Bad", "column_id": "missing"},
    )
    missing_card = board_client.patch(
        "/api/boards/user/cards/missing",
        headers=auth_headers(),
        json={"title": "Bad", "details": "Bad"},
    )
    invalid_payload = board_client.post(
        "/api/boards/user/cards/card-1/move",
        headers=auth_headers(),
        json={"column_id": "col-review", "position": -1},
    )

    assert missing_column.status_code == 404
    assert missing_card.status_code == 404
    assert invalid_payload.status_code == 422


def test_repeated_moves_preserve_board_order(board_client: TestClient) -> None:
    for _ in range(10):
        response = board_client.post(
            "/api/boards/user/cards/card-1/move",
            headers=auth_headers(),
            json={"column_id": "col-backlog", "position": 1},
        )
        assert response.status_code == 200

    for _ in range(10):
        response = board_client.post(
            "/api/boards/user/cards/card-1/move",
            headers=auth_headers(),
            json={"column_id": "col-review", "position": 0},
        )
        assert response.status_code == 200

    board = response.json()
    assert board["columns"][0]["cardIds"] == ["card-2"]
    assert board["columns"][3]["cardIds"] == ["card-1", "card-6"]
    assert sum(len(column["cardIds"]) for column in board["columns"]) == len(board["cards"])
