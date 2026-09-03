from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR.parent / "frontend" / "out"
if not STATIC_DIR.is_dir():
    STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Project Management MVP")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
