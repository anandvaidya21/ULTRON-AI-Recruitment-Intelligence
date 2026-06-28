"""
ULTRON AI – Analytics API Router
Yields structured aggregated statistics for frontend Chart.js graphics.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
import numpy as np

from database import crud
from database.database import get_db, CandidateDB, AnalysisDB

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("")
def get_analytics(db: Session = Depends(get_db)):
    """
    Returns analytics aggregates:
    - Skill distribution
    - Experience distribution
    - Top technologies count
    - Candidate score histogram values
    - Education levels breakdown
    """
    candidates = db.query(CandidateDB).all()

    # 1. Skill & Tech distributions
    all_skills = []
    education_levels = []
    experience_ranges = {
        "0-1 Year (Junior)": 0,
        "1-3 Years": 0,
        "3-5 Years (Mid)": 0,
        "5-8 Years (Senior)": 0,
        "8+ Years (Lead)": 0
    }

    for c in candidates:
        profile = c.parsed_profile or {}

        # Skills
        skills = profile.get("skills", []) + profile.get("technical_skills", [])
        all_skills.extend([s.title() for s in skills if s])

        # Education
        edu_entries = profile.get("education", [])
        for edu in edu_entries:
            deg = edu.get("degree", "").lower()
            if any(k in deg for k in ["b.tech", "b.e", "bachelor"]):
                education_levels.append("Bachelor's Degree")
            elif any(k in deg for k in ["m.tech", "m.e", "master"]):
                education_levels.append("Master's Degree")
            elif "phd" in deg or "doctor" in deg:
                education_levels.append("PhD / Doctorate")
            elif "diploma" in deg:
                education_levels.append("Diploma")

        # Experience
        exp = profile.get("total_experience_years", 0.0) or 0.0
        if exp <= 1.0:
            experience_ranges["0-1 Year (Junior)"] += 1
        elif exp <= 3.0:
            experience_ranges["1-3 Years"] += 1
        elif exp <= 5.0:
            experience_ranges["3-5 Years (Mid)"] += 1
        elif exp <= 8.0:
            experience_ranges["5-8 Years (Senior)"] += 1
        else:
            experience_ranges["8+ Years (Lead)"] += 1

    skill_counts = Counter(all_skills)
    top_skills = dict(skill_counts.most_common(12))

    edu_counts = Counter(education_levels)
    edu_breakdown = dict(edu_counts)

    # 2. Score histogram values
    analyses = db.query(AnalysisDB.overall_score).all()
    scores = [a[0] for a in analyses if a[0] is not None]

    score_histogram = {
        "0-20%": 0,
        "21-40%": 0,
        "41-60%": 0,
        "61-80%": 0,
        "81-100%": 0
    }
    for s in scores:
        if s <= 20:
            score_histogram["0-20%"] += 1
        elif s <= 40:
            score_histogram["21-40%"] += 1
        elif s <= 60:
            score_histogram["41-60%"] += 1
        elif s <= 80:
            score_histogram["61-80%"] += 1
        else:
            score_histogram["81-100%"] += 1

    # 3. Overall stats
    total_candidates = len(candidates)
    github_percentage = 0
    deployment_percentage = 0

    if total_candidates > 0:
        github_count = sum(1 for c in candidates if c.github_url or (c.parsed_profile and c.parsed_profile.get("open_source")))
        deploy_count = sum(1 for c in candidates if c.parsed_profile and c.parsed_profile.get("deployment_experience"))
        github_percentage = round((github_count / total_candidates) * 100, 1)
        deployment_percentage = round((deploy_count / total_candidates) * 100, 1)

    return {
        "skills_distribution": top_skills,
        "experience_distribution": experience_ranges,
        "education_distribution": edu_breakdown,
        "score_distribution": score_histogram,
        "insights": {
            "github_ratio": github_percentage,
            "deployment_ratio": deployment_percentage
        }
    }
