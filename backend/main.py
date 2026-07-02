"""
ULTRON AI – FastAPI Backend Entry Point
Launches server, mounts CORS headers, and includes API routers.
Mounts static files and enables startup table auto-creation.
"""

import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import database
from api import auth, jobs, resumes, candidates, rankings, chat, dashboard, analytics

app = FastAPI(
    title="ULTRON AI API",
    description="Semantic AI Recruitment Intelligence Platform API Gateway",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ultron-ai-recruitment-intelligence.vercel.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    database.create_tables()
    # Ensure upload directory exists
    os.makedirs("uploads", exist_ok=True)


# Include API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(rankings.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Basic status endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ULTRON AI Backend Platform",
        "api_docs": "/docs"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
