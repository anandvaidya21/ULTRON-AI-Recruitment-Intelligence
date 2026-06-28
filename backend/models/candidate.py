"""ULTRON AI – Pydantic Models for Candidates"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CandidateProfile(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    hackathons: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    total_experience_years: Optional[float] = None
    current_role: Optional[str] = None
    career_level: Optional[str] = None   # Junior / Mid / Senior / Lead
    industry_domains: List[str] = []
    open_source: bool = False
    deployment_experience: bool = False


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    parsed_profile: Optional[dict]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int
