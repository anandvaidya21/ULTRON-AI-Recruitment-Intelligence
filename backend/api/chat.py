"""
ULTRON AI – Chat API Router
Integrates the recruiter conversational assistant chatbot.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import crud
from database.database import get_db
from models.user import ChatRequest, ChatResponse
from services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Recruiter Chat Assistant"])


@router.post("", response_model=ChatResponse)
def chat_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Recruiter Chat Assistant.
    Recruiters ask questions about candidates (e.g., 'Find FastAPI developers' or 'Who fits startup culture?')
    and receive intelligent responses back.
    """
    try:
        chat_reply = chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            db=db,
            job_id=request.job_id
        )
        return chat_reply
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat generation failed: {str(e)}"
        )
