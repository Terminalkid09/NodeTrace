import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Rate limiting
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.utils.ratelimit import limiter

# Router
from app.api.v1.endpoints import router as api_router
from app.api.v1.auth import router as auth_router

# Database
from app.database.base import Base
from app.database.connection import engine

# Database initialization
if os.getenv("SKIP_DB_CREATE", "false").lower() not in ("1", "true", "yes"):
    Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(
    title="NodeTrace Backend",
    description="Backend API for NodeTrace Monitoring System",
    version="1.0.0"
)

# CORS (frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: SECURITY - Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"status": "error", "message": "rate_limit_exceeded"}
    )

# Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/auth")

# Root endpoint
@app.get("/")
def root():
    return {"message": "NodeTrace API is running"}