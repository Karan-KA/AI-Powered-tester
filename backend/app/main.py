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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REACT_DIST = PROJECT_ROOT / "frontend" / "dist"
REACT_INDEX = REACT_DIST / "index.html"

if (REACT_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=REACT_DIST / "assets"), name="react-assets")

if Path(settings.artifacts_dir).exists():
    app.mount("/artifacts", StaticFiles(directory=settings.artifacts_dir), name="artifacts")


@app.get("/")
def home():
    return chatbot_app()


@app.get("/app")
def chatbot_app():
    if not REACT_INDEX.exists():
        return {
            "message": "React frontend file is missing.",
            "expected_file": str(REACT_INDEX),
        }

    return FileResponse(
        REACT_INDEX,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )

