"""
ULTRON AI – Resume Upload API Router
Handles file uploads, text extraction, profile building, and initial parsing.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from typing import List

from database import crud
from database.database import get_db
from models.candidate import CandidateResponse
from services.resume_parser import ResumeParser
from services.embedding_service import embedding_service
from utils.text_extractor import extract_text_from_bytes

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize parser without AI service (it will fall back to rule-based parser or inject AI if active)
# In standard startup, we'll configure parser properly
resume_parser = ResumeParser()


@router.post("/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and automatically parse a candidate resume (.pdf, .docx, .txt).
    Builds a structured Candidate Profile, generates embeddings, and saves to database.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {ext}. Only PDF, DOCX, and TXT are supported."
        )

    # 1. Read file bytes
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )

    # 2. Extract raw text
    try:
        raw_text = extract_text_from_bytes(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text from resume: {str(e)}"
        )

    # 3. Parse resume semantically
    try:
        parsed_profile = resume_parser.parse(raw_text, filename=file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )

    # Save physical file to uploads/ for future download
    file_path = UPLOAD_DIR / f"{parsed_profile.get('name', 'candidate').replace(' ', '_')}_{file.filename}"
    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        # Log error, continue since DB save is more critical
        pass

    # 4. Generate profile embedding
    text_to_embed = f"{parsed_profile.get('name', '')} {parsed_profile.get('summary', '')} " \
                    f"{' '.join(parsed_profile.get('skills', []))} " \
                    f"{parsed_profile.get('current_role', '')} {parsed_profile.get('career_level', '')} " \
                    f"{' '.join([p.get('name', '') + ' ' + p.get('description', '') for p in parsed_profile.get('projects', [])])}"

    emb = embedding_service.get_embedding(text_to_embed)
    emb_str = embedding_service.serialize(emb) if emb is not None else "[]"

    # 5. Check if duplicate email exists
    email = parsed_profile.get("email")
    if email:
        existing = crud.get_candidate_by_email(db, email)
        if existing:
            # Update existing candidate instead of duplicating
            existing.parsed_profile = parsed_profile
            existing.raw_text = raw_text
            existing.embedding = emb_str
            existing.resume_path = str(file_path)
            existing.github_url = parsed_profile.get("github_url") or existing.github_url
            existing.linkedin_url = parsed_profile.get("linkedin_url") or existing.linkedin_url
            existing.portfolio_url = parsed_profile.get("portfolio_url") or existing.portfolio_url
            db.commit()
            db.refresh(existing)
            return existing

    # Create new Candidate
    candidate = crud.create_candidate(
        db,
        name=parsed_profile.get("name", "Unknown Candidate"),
        email=email,
        phone=parsed_profile.get("phone"),
        resume_path=str(file_path),
        raw_text=raw_text,
        parsed_profile=parsed_profile,
        embedding=emb_str,
        github_url=parsed_profile.get("github_url"),
        linkedin_url=parsed_profile.get("linkedin_url"),
        portfolio_url=parsed_profile.get("portfolio_url")
    )

    return candidate
