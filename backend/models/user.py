"""ULTRON AI – Pydantic Models for Users & Authentication"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str = Field(..., description="Recruiter email")
    full_name: str = Field(..., description="Full name")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    company: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChatRequest(BaseModel):
    message: str = Field(..., description="Recruiter's question")
    session_id: str = Field(default="default", description="Chat session ID")
    job_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    candidates_mentioned: Optional[list] = []
    session_id: str
    suggestions: Optional[list] = []
