"""ULTRON AI – Pydantic Models for Analysis & Scoring"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScoreBreakdown(BaseModel):
    overall: float = 0.0
    skills: float = 0.0
    projects: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    soft_skills: float = 0.0
    industry: float = 0.0
    growth: float = 0.0
    github: float = 0.0
    portfolio: float = 0.0
    certifications: float = 0.0


class ExplainabilityReport(BaseModel):
    overall_match_percent: float
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_skills: List[str] = []
    why_ranked_here: str = ""
    interview_recommendation: str = ""
    hiring_recommendation: str = ""
    risk_analysis: str = ""
    confidence_score: float = 0.0
    score_breakdown: ScoreBreakdown = ScoreBreakdown()
    semantic_similarity: float = 0.0


class AnalysisRequest(BaseModel):
    job_id: int
    candidate_ids: Optional[List[int]] = None  # None = analyze all candidates


class RankedCandidate(BaseModel):
    rank: int
    candidate_id: int
    candidate_name: str
    candidate_email: Optional[str]
    overall_score: float
    score_breakdown: ScoreBreakdown
    explainability: ExplainabilityReport
    parsed_profile: Optional[dict]


class RankingResponse(BaseModel):
    job_id: int
    job_title: str
    total_candidates: int
    rankings: List[RankedCandidate]
    analysis_timestamp: datetime


class AnalysisResponse(BaseModel):
    success: bool
    job_id: int
    candidates_analyzed: int
    message: str
