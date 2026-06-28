"""
ULTRON AI – Rankings & Matching API Router
Executes semantic matching engine, scores candidates, and yields explainable rankings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np

from database import crud
from database.database import get_db
from models.analysis import AnalysisRequest, AnalysisResponse, RankingResponse, RankedCandidate
from services.matching_engine import matching_engine
from services.scoring_engine import scoring_engine
from services.embedding_service import embedding_service

router = APIRouter(tags=["Rankings"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_candidates(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Compare Job Description vs Candidates using Semantic matching.
    Runs matching and explainable scoring engines for target candidates.
    """
    job = crud.get_job(db, request.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {request.job_id} not found"
        )

    # Decode job embedding
    job_emb = embedding_service.deserialize(job.embedding) if job.embedding else None

    # Get target candidates
    if request.candidate_ids:
        candidates = [crud.get_candidate(db, cid) for cid in request.candidate_ids]
        candidates = [c for c in candidates if c is not None]
    else:
        candidates = crud.get_all_candidates(db)

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidates available to analyze. Please upload resumes first."
        )

    analyzed_count = 0

    for candidate in candidates:
        # Decode candidate embedding
        cand_emb = embedding_service.deserialize(candidate.embedding) if candidate.embedding else None

        # 1. Semantic Cosine Similarity & Multi-dimensional matching
        scores = matching_engine.match(
            job.parsed_data or {},
            candidate.parsed_profile or {},
            job_embedding=job_emb,
            candidate_embedding=cand_emb
        )

        # 2. Explainable scoring (strengths, weaknesses, recommendations)
        analysis_report = scoring_engine.generate_report(
            job.parsed_data or {},
            candidate.parsed_profile or {},
            scores
        )

        # 3. Save/Update Analysis in DB
        existing_analysis = crud.get_analysis(db, job.id, candidate.id)
        if existing_analysis:
            existing_analysis.overall_score = scores.get("overall", 0)
            existing_analysis.skill_score = scores.get("skills", 0)
            existing_analysis.project_score = scores.get("projects", 0)
            existing_analysis.experience_score = scores.get("experience", 0)
            existing_analysis.education_score = scores.get("education", 0)
            existing_analysis.soft_skill_score = scores.get("soft_skills", 0)
            existing_analysis.industry_score = scores.get("industry", 0)
            existing_analysis.growth_score = scores.get("growth", 0)
            existing_analysis.github_score = scores.get("github", 0)
            existing_analysis.portfolio_score = scores.get("portfolio", 0)
            existing_analysis.analysis_data = analysis_report
            existing_analysis.created_at = datetime.utcnow()
        else:
            crud.create_analysis(db, job.id, candidate.id, scores, analysis_report)

        analyzed_count += 1

    db.commit()

    return {
        "success": True,
        "job_id": job.id,
        "candidates_analyzed": analyzed_count,
        "message": f"Successfully matched and analyzed {analyzed_count} candidates."
    }


@router.get("/rankings/{job_id}", response_model=RankingResponse)
def get_rankings(job_id: int, db: Session = Depends(get_db)):
    """Get sorted list of candidate rankings with full explainability details."""
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {job_id} not found"
        )

    # Fetch matching analyses sorted by score descending
    analyses = crud.get_rankings_for_job(db, job_id)

    ranked_candidates = []
    for rank_idx, analysis in enumerate(analyses):
        candidate = crud.get_candidate(db, analysis.candidate_id)
        if not candidate:
            continue

        explainability = analysis.analysis_data or {}
        # Make sure breakdown is present
        breakdown = explainability.get("score_breakdown", {})

        ranked_candidates.append(
            RankedCandidate(
                rank=rank_idx + 1,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                overall_score=analysis.overall_score or 0.0,
                score_breakdown=breakdown,
                explainability=explainability,
                parsed_profile=candidate.parsed_profile
            )
        )

    return {
        "job_id": job.id,
        "job_title": job.title,
        "total_candidates": len(ranked_candidates),
        "rankings": ranked_candidates,
        "analysis_timestamp": datetime.utcnow()
    }
