"""ULTRON AI – Database CRUD Operations"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import JobDB, CandidateDB, AnalysisDB, UserDB, ChatMessageDB
from datetime import datetime
from typing import Optional, List
import json


# ------------------------------------------------------------------
# User CRUD
# ------------------------------------------------------------------

def create_user(db: Session, email: str, full_name: str, hashed_password: str,
                company: str = None) -> UserDB:
    user = UserDB(email=email, full_name=full_name, hashed_password=hashed_password,
                  company=company)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.id == user_id).first()


# ------------------------------------------------------------------
# Job CRUD
# ------------------------------------------------------------------

def create_job(db: Session, title: str, company: str, raw_description: str,
               parsed_data: dict = None, embedding: str = None,
               created_by: int = None) -> JobDB:
    job = JobDB(
        title=title, company=company, raw_description=raw_description,
        parsed_data=parsed_data, embedding=embedding, created_by=created_by
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: int) -> Optional[JobDB]:
    return db.query(JobDB).filter(JobDB.id == job_id).first()


def get_all_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[JobDB]:
    return db.query(JobDB).order_by(desc(JobDB.created_at)).offset(skip).limit(limit).all()


def update_job_embedding(db: Session, job_id: int, embedding: str):
    db.query(JobDB).filter(JobDB.id == job_id).update({"embedding": embedding})
    db.commit()


# ------------------------------------------------------------------
# Candidate CRUD
# ------------------------------------------------------------------

def create_candidate(db: Session, name: str, email: str = None, phone: str = None,
                     resume_path: str = None, raw_text: str = None,
                     parsed_profile: dict = None, embedding: str = None,
                     github_url: str = None, linkedin_url: str = None,
                     portfolio_url: str = None) -> CandidateDB:
    candidate = CandidateDB(
        name=name, email=email, phone=phone, resume_path=resume_path,
        raw_text=raw_text, parsed_profile=parsed_profile, embedding=embedding,
        github_url=github_url, linkedin_url=linkedin_url, portfolio_url=portfolio_url
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_candidate(db: Session, candidate_id: int) -> Optional[CandidateDB]:
    return db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()


def get_all_candidates(db: Session, skip: int = 0, limit: int = 200) -> List[CandidateDB]:
    return db.query(CandidateDB).order_by(desc(CandidateDB.created_at)).offset(skip).limit(limit).all()


def get_candidate_by_email(db: Session, email: str) -> Optional[CandidateDB]:
    return db.query(CandidateDB).filter(CandidateDB.email == email).first()


# ------------------------------------------------------------------
# Analysis CRUD
# ------------------------------------------------------------------

def create_analysis(db: Session, job_id: int, candidate_id: int,
                    scores: dict, analysis_data: dict) -> AnalysisDB:
    analysis = AnalysisDB(
        job_id=job_id, candidate_id=candidate_id,
        overall_score=scores.get("overall", 0),
        skill_score=scores.get("skills", 0),
        project_score=scores.get("projects", 0),
        experience_score=scores.get("experience", 0),
        education_score=scores.get("education", 0),
        soft_skill_score=scores.get("soft_skills", 0),
        industry_score=scores.get("industry", 0),
        growth_score=scores.get("growth", 0),
        github_score=scores.get("github", 0),
        portfolio_score=scores.get("portfolio", 0),
        analysis_data=analysis_data
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_rankings_for_job(db: Session, job_id: int) -> List[AnalysisDB]:
    return (db.query(AnalysisDB)
            .filter(AnalysisDB.job_id == job_id)
            .order_by(desc(AnalysisDB.overall_score))
            .all())


def get_analysis(db: Session, job_id: int, candidate_id: int) -> Optional[AnalysisDB]:
    return (db.query(AnalysisDB)
            .filter(AnalysisDB.job_id == job_id, AnalysisDB.candidate_id == candidate_id)
            .first())


def get_all_analyses(db: Session, job_id: int = None) -> List[AnalysisDB]:
    q = db.query(AnalysisDB)
    if job_id:
        q = q.filter(AnalysisDB.job_id == job_id)
    return q.order_by(desc(AnalysisDB.overall_score)).all()


# ------------------------------------------------------------------
# Chat CRUD
# ------------------------------------------------------------------

def save_chat_message(db: Session, session_id: str, role: str,
                      content: str, chat_metadata: dict = None) -> ChatMessageDB:
    msg = ChatMessageDB(session_id=session_id, role=role, content=content, chat_metadata=chat_metadata)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(db: Session, session_id: str, limit: int = 20) -> List[ChatMessageDB]:
    return (db.query(ChatMessageDB)
            .filter(ChatMessageDB.session_id == session_id)
            .order_by(ChatMessageDB.created_at)
            .limit(limit)
            .all())
