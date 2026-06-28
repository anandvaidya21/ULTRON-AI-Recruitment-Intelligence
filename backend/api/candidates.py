"""
ULTRON AI – Candidates API Router
Handles candidate profile list, detailed profile builder, and resume download.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from database import crud
from database.database import get_db
from models.candidate import CandidateResponse, CandidateListResponse

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("", response_model=CandidateListResponse)
def get_candidates(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    """List all candidate profiles."""
    candidates = crud.get_all_candidates(db, skip=skip, limit=limit)
    return {
        "candidates": candidates,
        "total": len(candidates)
    }


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get complete Candidate Profile (Resume details + Career timeline)."""
    candidate = crud.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    return candidate


@router.get("/{candidate_id}/download-resume")
def download_resume(candidate_id: int, db: Session = Depends(get_db)):
    """Download the original uploaded resume file."""
    candidate = crud.get_candidate(db, candidate_id)
    if not candidate or not candidate.resume_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found for this candidate"
        )

    file_path = candidate.resume_path
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file does not exist on disk"
        )

    # Extract original filename
    original_filename = os.path.basename(file_path)
    if "_" in original_filename:
        # Strip name prefix if saved by upload route
        original_filename = original_filename.split("_", 1)[1]

    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type="application/octet-stream"
    )
