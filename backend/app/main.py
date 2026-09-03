from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.staticfiles import StaticFiles

from app import database
from app.schemas import CardCreate, CardMove, CardUpdate, ColumnUpdate


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR.parent / "frontend" / "out"
if not STATIC_DIR.is_dir():
    STATIC_DIR = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(_: FastAPI):
    database.initialize_database()
    yield


app = FastAPI(title="Project Management MVP", lifespan=lifespan)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def require_user(username: str, x_username: str | None = Header(default=None)) -> str:
    if x_username != username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return username


def board_or_404(username: str) -> dict:
    board = database.get_board(username)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


@app.get("/api/boards/{username}")
def read_board(username: str, _: str = Depends(require_user)) -> dict:
    return board_or_404(username)


@app.patch("/api/boards/{username}/columns/{column_id}")
def rename_column(
    username: str,
    column_id: str,
    payload: ColumnUpdate,
    _: str = Depends(require_user),
) -> dict:
    if not database.rename_column(username, column_id, payload.title):
        raise HTTPException(status_code=404, detail="Column not found")
    return board_or_404(username)


@app.post("/api/boards/{username}/cards", status_code=201)
def add_card(
    username: str,
    payload: CardCreate,
    _: str = Depends(require_user),
) -> dict:
    try:
        created = database.create_card(
            username, payload.id, payload.title, payload.details, payload.column_id
        )
    except Exception as error:
        if "UNIQUE constraint failed: cards.id" not in str(error):
            raise
        raise HTTPException(status_code=409, detail="Card already exists") from error
    if not created:
        raise HTTPException(status_code=404, detail="Column not found")
    return board_or_404(username)


@app.patch("/api/boards/{username}/cards/{card_id}")
def edit_card(
    username: str,
    card_id: str,
    payload: CardUpdate,
    _: str = Depends(require_user),
) -> dict:
    if not database.update_card(username, card_id, payload.title, payload.details):
        raise HTTPException(status_code=404, detail="Card not found")
    return board_or_404(username)


@app.delete("/api/boards/{username}/cards/{card_id}")
def remove_card(
    username: str,
    card_id: str,
    _: str = Depends(require_user),
) -> dict:
    if not database.delete_card(username, card_id):
        raise HTTPException(status_code=404, detail="Card not found")
    return board_or_404(username)


@app.post("/api/boards/{username}/cards/{card_id}/move")
def move_board_card(
    username: str,
    card_id: str,
    payload: CardMove,
    _: str = Depends(require_user),
) -> dict:
    if not database.move_card(username, card_id, payload.column_id, payload.position):
        raise HTTPException(status_code=404, detail="Card or column not found")
    return board_or_404(username)


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
