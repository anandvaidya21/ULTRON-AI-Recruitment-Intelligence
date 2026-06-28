"""
ULTRON AI – Jobs API Router
Handles job description creation, list retrieval, and detailed insights.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import crud
from database.database import get_db
from models.job import JobCreate, JobResponse, JobListResponse
from services.job_analyzer import job_analyzer
from services.embedding_service import embedding_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def upload_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """
    Create a new Job.
    Runs raw description through the AI Job Understanding Engine.
    Generates semantic embedding for semantic matching.
    """
    # 1. Analyze Job Description using semantic engine
    try:
        parsed_data = job_analyzer.analyze(job_in.raw_description, title=job_in.title, company=job_in.company)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze job description: {str(e)}"
        )

    # 2. Generate embedding of parsed details
    text_to_embed = f"{parsed_data.get('title', '')} {parsed_data.get('role_summary', '')} " \
                    f"{' '.join(parsed_data.get('required_skills', []))} " \
                    f"{parsed_data.get('experience_years', '')} {parsed_data.get('domain', '')}"
    
    emb = embedding_service.get_embedding(text_to_embed)
    emb_str = embedding_service.serialize(emb) if emb is not None else "[]"

    # 3. Save to database
    job = crud.create_job(
        db,
        title=parsed_data.get("title", job_in.title),
        company=parsed_data.get("company", job_in.company or "Recruiter's Company"),
        raw_description=job_in.raw_description,
        parsed_data=parsed_data,
        embedding=emb_str
    )

    return job


@router.get("", response_model=JobListResponse)
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all job descriptions."""
    jobs = crud.get_all_jobs(db, skip=skip, limit=limit)
    return {
        "jobs": jobs,
        "total": len(jobs)
    }


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get detailed job description by ID."""
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    return job
