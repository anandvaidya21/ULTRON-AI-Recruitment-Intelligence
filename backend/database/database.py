"""
ULTRON AI – Database Configuration
Supports SQLite (default) and PostgreSQL (via DATABASE_URL env var).
SQLAlchemy ORM for clean abstraction and easy migration.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ------------------------------------------------------------------
# Connection Setup – swap DATABASE_URL to switch to PostgreSQL
# ------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ultron_ai.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ------------------------------------------------------------------
# ORM Models
# ------------------------------------------------------------------

class UserDB(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True)
    email       = Column(String(255), unique=True, index=True, nullable=False)
    full_name   = Column(String(255), nullable=False)
    hashed_password = Column(String(512), nullable=False)
    company     = Column(String(255), nullable=True)
    role        = Column(String(50), default="recruiter")
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


class JobDB(Base):
    __tablename__ = "jobs"

    id              = Column(Integer, primary_key=True, index=True)
    title           = Column(String(255), nullable=False)
    company         = Column(String(255), nullable=True)
    raw_description = Column(Text, nullable=False)
    parsed_data     = Column(JSON, nullable=True)   # Structured JD JSON
    embedding       = Column(Text, nullable=True)   # Serialized numpy array
    status          = Column(String(50), default="active")
    created_at      = Column(DateTime, default=datetime.utcnow)
    created_by      = Column(Integer, nullable=True)


class CandidateDB(Base):
    __tablename__ = "candidates"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(255), nullable=False)
    email           = Column(String(255), nullable=True, index=True)
    phone           = Column(String(50), nullable=True)
    resume_path     = Column(String(512), nullable=True)
    raw_text        = Column(Text, nullable=True)
    parsed_profile  = Column(JSON, nullable=True)  # Full structured profile
    embedding       = Column(Text, nullable=True)  # Serialized numpy array
    github_url      = Column(String(512), nullable=True)
    linkedin_url    = Column(String(512), nullable=True)
    portfolio_url   = Column(String(512), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)


class AnalysisDB(Base):
    __tablename__ = "analyses"

    id              = Column(Integer, primary_key=True, index=True)
    job_id          = Column(Integer, nullable=False, index=True)
    candidate_id    = Column(Integer, nullable=False, index=True)
    overall_score   = Column(Float, nullable=True)
    skill_score     = Column(Float, nullable=True)
    project_score   = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    soft_skill_score = Column(Float, nullable=True)
    industry_score  = Column(Float, nullable=True)
    growth_score    = Column(Float, nullable=True)
    github_score    = Column(Float, nullable=True)
    portfolio_score = Column(Float, nullable=True)
    analysis_data   = Column(JSON, nullable=True)  # Full explainability JSON
    rank            = Column(Integer, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)


class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id          = Column(Integer, primary_key=True, index=True)
    session_id  = Column(String(100), nullable=False, index=True)
    role        = Column(String(20), nullable=False)  # user / assistant
    content     = Column(Text, nullable=False)
    chat_metadata = Column(JSON, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def get_db():
    """FastAPI dependency – yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables on startup."""
    Base.metadata.create_all(bind=engine)
