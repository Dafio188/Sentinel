from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.core.security import SESSION_TOKEN, verify_session_middleware
from backend.app.db.engine import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize SQLite database with DDL v0.1 & seed providers
    init_db()
    print(f"==================================================")
    print(f" AIGate Backend Started on http://{settings.HOST}:{settings.PORT}")
    print(f" Session Token: {SESSION_TOKEN}")
    print(f"==================================================")
    yield

app = FastAPI(
    title="AIGate - Local AI Privacy & Compliance Gateway",
    lifespan=lifespan,
    docs_url=None,  # Disabled public swagger for security
    redoc_url=None,
)

# Custom session token middleware
app.middleware("http")(verify_session_middleware)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Include API router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # Hard-coded binding strictly on 127.0.0.1 (Invariant)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=settings.PORT, reload=False)
