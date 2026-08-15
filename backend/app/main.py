from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_tests import router as tests_router
from app.core.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-assisted platform for generating, executing, and analyzing web application tests.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later change this to React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tests_router)

def resolve_react_index() -> Path:
    candidates = [
        Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html",
        Path(__file__).resolve().parents[1] / "frontend" / "dist" / "index.html",
        Path(__file__).resolve().parents[0] / "frontend" / "dist" / "index.html",
        Path("/app/frontend/dist/index.html"),
        Path("frontend/dist/index.html"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


REACT_INDEX = resolve_react_index()
REACT_DIST = REACT_INDEX.parent

if (REACT_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=REACT_DIST / "assets"), name="react-assets")

if Path(settings.artifacts_dir).exists():
    app.mount("/artifacts", StaticFiles(directory=settings.artifacts_dir), name="artifacts")


@app.get("/")
def home():
    return chatbot_app()


@app.get("/app")
def chatbot_app():
    target_index = resolve_react_index()
    if not target_index.exists():
        return {
            "message": "Frontend index file is missing.",
            "expected_file": str(target_index),
        }

    return FileResponse(
        target_index,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


