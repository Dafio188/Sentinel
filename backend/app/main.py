from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.router import router as api_router
from backend.app.core.config import settings
from backend.app.core.security import verify_session_middleware
from backend.app.db.engine import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="AIGate — Local AI Privacy & Compliance Gateway",
    version="0.6.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# CORS middleware allowing local frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/health", "/api/health"]:
        response = await call_next(request)
    else:
        response = await verify_session_middleware(request, call_next)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

app.include_router(api_router, prefix="/api")
