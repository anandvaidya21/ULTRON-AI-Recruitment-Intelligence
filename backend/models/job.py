"""ULTRON AI – Pydantic Models for Jobs"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JobCreate(BaseModel):
    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    raw_description: str = Field(..., description="Raw job description text")


class JobParsed(BaseModel):
    title: str
    company: Optional[str] = None
    role_summary: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_years: Optional[str] = None
    education: Optional[str] = None
    responsibilities: List[str] = []
    soft_skills: List[str] = []
    domain: Optional[str] = None
    industry: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    tech_stack: List[str] = []
    seniority_level: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    parsed_data: Optional[dict]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
