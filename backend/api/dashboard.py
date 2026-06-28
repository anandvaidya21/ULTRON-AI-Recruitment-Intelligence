"""
ULTRON AI – Dashboard API Router
Returns high-level stats and KPIs for recruiter dashboard.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import crud
from database.database import get_db, JobDB, CandidateDB, AnalysisDB

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns high level KPIs:
    - Total Jobs
    - Total Candidates
    - Matches Analyzed
    - Average Match Score
    - Top matches list
    - Recent uploads (resumes & jobs)
    """
    total_jobs = db.query(JobDB).count()
    total_candidates = db.query(CandidateDB).count()
    total_analyses = db.query(AnalysisDB).count()

    # Avg match score
    avg_score = db.query(func.avg(AnalysisDB.overall_score)).scalar() or 0.0
    avg_score = round(float(avg_score), 1)

    # Top matches
    top_matches = []
    analyses = db.query(AnalysisDB).order_by(AnalysisDB.overall_score.desc()).limit(5).all()
    for a in analyses:
        candidate = crud.get_candidate(db, a.candidate_id)
        job = crud.get_job(db, a.job_id)
        if candidate and job:
            top_matches.append({
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "job_id": job.id,
                "job_title": job.title,
                "match_score": a.overall_score
            })

    # Recent resumes
    recent_resumes = []
    candidates = db.query(CandidateDB).order_by(CandidateDB.created_at.desc()).limit(5).all()
    for c in candidates:
        profile = c.parsed_profile or {}
        recent_resumes.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "role": profile.get("current_role") or "Not specified",
            "experience": profile.get("total_experience_years") or 0.0,
            "uploaded_at": c.created_at.isoformat()
        })

    # Recent jobs
    recent_jobs = []
    jobs = db.query(JobDB).order_by(JobDB.created_at.desc()).limit(5).all()
    for j in jobs:
        recent_jobs.append({
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "status": j.status,
            "created_at": j.created_at.isoformat()
        })

    # AI Insights summary
    insights = []
    if total_candidates > 0:
        insights.append(f"Analyzing {total_candidates} candidate profiles across {total_jobs} active job requirements.")
    else:
        insights.append("Welcome! Getting started: Upload a job description and candidates' resumes to see AI recruiter matches.")

    if total_analyses > 0:
        top_fit = top_matches[0]["candidate_name"] if top_matches else "a candidate"
        insights.append(f"Match evaluation completed. {top_fit} shows the highest semantic alignment.")

    return {
        "kpis": {
            "total_jobs": total_jobs,
            "total_candidates": total_candidates,
            "matches_analyzed": total_analyses,
            "average_match_score": avg_score
        },
        "top_matches": top_matches,
        "recent_resumes": recent_resumes,
        "recent_jobs": recent_jobs,
        "ai_insights": insights
    }
