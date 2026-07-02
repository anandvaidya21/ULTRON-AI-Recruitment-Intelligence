"""
ULTRON AI – Rankings & Matching API Router
Executes semantic matching engine, scores candidates, and yields explainable rankings.
"""
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import csv
import io


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


@router.get("/rankings/{job_id}/export")
def export_rankings(job_id: int, db: Session = Depends(get_db)):

    job = crud.get_job(db, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    analyses = crud.get_rankings_for_job(db, job_id)

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Rank",
        "Candidate Name",
        "Email",
        "Overall Score",
        "Skill Score",
        "Experience Score",
        "Project Score",
        "Education Score",
        "Industry Score",
        "Soft Skill Score",
        "Growth Score",
        "GitHub Score",
        "Portfolio Score"
    ])

    for rank, analysis in enumerate(analyses, start=1):

        candidate = crud.get_candidate(db, analysis.candidate_id)

        writer.writerow([
            rank,
            candidate.name if candidate else "",
            candidate.email if candidate else "",
            analysis.overall_score,
            analysis.skill_score,
            analysis.experience_score,
            analysis.project_score,
            analysis.education_score,
            analysis.industry_score,
            analysis.soft_skill_score,
            analysis.growth_score,
            analysis.github_score,
            analysis.portfolio_score
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=candidate_rankings_job_{job_id}.csv"
        }
    )
