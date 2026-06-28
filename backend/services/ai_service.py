"""
ULTRON AI – AI Service
Unified interface for LLM integrations.
Priority: Gemini → OpenAI → Rule-based fallback (always works offline).
"""

import os
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AIService:
    """
    Abstraction layer for LLM APIs.
    Automatically detects available APIs and uses the best one.
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self._gemini_model = None
        self._openai_client = None
        self._provider = self._detect_provider()

    def _detect_provider(self) -> str:
        """Detect which AI provider is available."""
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self._gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                logger.info("AI Provider: Google Gemini")
                return "gemini"
            except Exception as e:
                logger.warning(f"Gemini setup failed: {e}")

        if self.openai_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.openai_key)
                logger.info("AI Provider: OpenAI")
                return "openai"
            except Exception as e:
                logger.warning(f"OpenAI setup failed: {e}")

        logger.info("AI Provider: Rule-based (no API keys provided)")
        return "rule_based"

    def get_provider(self) -> str:
        return self._provider

    # ------------------------------------------------------------------
    # Resume Parsing via LLM
    # ------------------------------------------------------------------

    def parse_resume(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Use LLM to parse resume into structured JSON."""
        prompt = self._resume_parse_prompt(raw_text[:3000])

        if self._provider == "gemini":
            return self._gemini_parse(prompt)
        elif self._provider == "openai":
            return self._openai_parse(prompt)
        return None

    # ------------------------------------------------------------------
    # Job Description Analysis via LLM
    # ------------------------------------------------------------------

    def analyze_job_description(self, raw_jd: str) -> Optional[Dict[str, Any]]:
        """Use LLM to analyze JD into structured JSON."""
        prompt = self._jd_analysis_prompt(raw_jd[:3000])

        if self._provider == "gemini":
            return self._gemini_parse(prompt)
        elif self._provider == "openai":
            return self._openai_parse(prompt)
        return None

    # ------------------------------------------------------------------
    # Chat / Q&A
    # ------------------------------------------------------------------

    def chat(self, message: str, context: str = "") -> str:
        """Generate a conversational AI response."""
        prompt = f"{context}\n\nRecruiter Question: {message}\n\nRespond as ULTRON AI recruiter assistant:"

        if self._provider == "gemini":
            return self._gemini_chat(prompt)
        elif self._provider == "openai":
            return self._openai_chat(prompt)
        return self._rule_based_chat(message, context)

    # ------------------------------------------------------------------
    # Gemini Implementations
    # ------------------------------------------------------------------

    def _gemini_parse(self, prompt: str) -> Optional[Dict]:
        """Call Gemini and parse JSON response."""
        try:
            response = self._gemini_model.generate_content(prompt)
            text = response.text
            return self._extract_json(text)
        except Exception as e:
            logger.error(f"Gemini parse error: {e}")
            return None

    def _gemini_chat(self, prompt: str) -> str:
        """Call Gemini for chat."""
        try:
            response = self._gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return self._rule_based_chat(prompt, "")

    # ------------------------------------------------------------------
    # OpenAI Implementations
    # ------------------------------------------------------------------

    def _openai_parse(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI and parse JSON response."""
        try:
            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert AI recruiter. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            text = response.choices[0].message.content
            return self._extract_json(text)
        except Exception as e:
            logger.error(f"OpenAI parse error: {e}")
            return None

    def _openai_chat(self, prompt: str) -> str:
        """Call OpenAI for chat."""
        try:
            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are ULTRON AI, an expert AI recruiter assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            return self._rule_based_chat(prompt, "")

    # ------------------------------------------------------------------
    # Rule-based Fallback
    # ------------------------------------------------------------------

    def _rule_based_chat(self, message: str, context: str) -> str:
        """Rule-based chatbot fallback when no LLM API is available."""
        msg_lower = message.lower()

        if any(kw in msg_lower for kw in ["best", "top", "highest", "rank"]):
            return ("Based on semantic analysis, I've ranked the candidates by their overall match score. "
                    "The top-ranked candidates show the strongest alignment with the job requirements "
                    "across skills, experience, and project relevance. Check the Rankings dashboard for details.")

        elif any(kw in msg_lower for kw in ["python", "javascript", "java", "react", "ml", "ai"]):
            skill = next((kw for kw in ["python", "javascript", "java", "react", "ml", "ai"]
                         if kw in msg_lower), "the requested skill")
            return (f"I'll search for candidates with strong {skill} skills. "
                    "Use the Candidates filter on the Candidates page to filter by specific skills. "
                    "The AI ranking system automatically scores technical skill alignment.")

        elif any(kw in msg_lower for kw in ["experience", "years", "senior", "junior"]):
            return ("I can help you filter candidates by experience level. "
                    "Our semantic matching engine considers total years of experience and career progression. "
                    "Use the filters on the Rankings or Candidates page to narrow by experience level.")

        elif any(kw in msg_lower for kw in ["deploy", "docker", "devops", "cloud"]):
            return ("Deployment experience is a scored dimension in our AI analysis. "
                    "Candidates with Docker, Kubernetes, or cloud platform experience "
                    "receive bonus points in the growth and skills dimensions.")

        elif any(kw in msg_lower for kw in ["github", "portfolio", "project"]):
            return ("GitHub and portfolio links are automatically extracted from resumes and scored. "
                    "Candidates with active GitHub profiles receive bonus points in our ranking. "
                    "Check the Candidate Detail page to see individual project portfolios.")

        elif any(kw in msg_lower for kw in ["startup", "culture", "fit"]):
            return ("Cultural fit assessment looks at: hackathon participation, open-source contributions, "
                    "project diversity, and deployment experience. "
                    "Candidates scoring high on Growth and GitHub dimensions tend to fit startup culture well.")

        elif any(kw in msg_lower for kw in ["hello", "hi", "hey"]):
            return ("Hello! I'm ULTRON AI, your intelligent recruitment assistant. "
                    "Ask me to find candidates by skill, experience, or background. "
                    "I can help you understand the ranking results and recommend the best fits.")

        else:
            return (f"I understand you're looking for information about: '{message}'. "
                    "As ULTRON AI, I analyze candidates semantically and can help you find the best matches. "
                    "Try asking about specific skills, experience levels, or cultural fit. "
                    "For detailed analysis, check the Rankings and Analytics dashboards.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from LLM response."""
        import re
        # Try markdown code block first
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except Exception:
                pass
        # Try raw JSON
        try:
            return json.loads(text.strip())
        except Exception:
            pass
        # Try to find JSON object
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None

    def _resume_parse_prompt(self, text: str) -> str:
        return f"""Extract structured information from this resume and return ONLY valid JSON.

Resume Text:
{text}

Return this exact JSON structure:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "city, country",
    "summary": "professional summary",
    "skills": ["skill1", "skill2"],
    "technical_skills": ["tech1", "tech2"],
    "soft_skills": ["communication", "teamwork"],
    "experience": [
        {{"role": "Job Title", "company": "Company", "duration": "2020-2022", "description": "..."}}
    ],
    "education": [
        {{"degree": "B.Tech CS", "institution": "University", "year": "2020", "grade": "8.5 CGPA"}}
    ],
    "projects": [
        {{"name": "Project Name", "description": "...", "technologies": ["tech1"]}}
    ],
    "certifications": ["cert1"],
    "hackathons": ["hackathon1"],
    "achievements": ["achievement1"],
    "languages": ["English", "Hindi"],
    "github_url": "https://github.com/...",
    "linkedin_url": "https://linkedin.com/...",
    "portfolio_url": "https://...",
    "total_experience_years": 3.0,
    "current_role": "Software Engineer",
    "career_level": "Mid-level"
}}"""

    def _jd_analysis_prompt(self, text: str) -> str:
        return f"""Analyze this job description and return ONLY valid JSON.

Job Description:
{text}

Return this exact JSON structure:
{{
    "title": "Job Title",
    "company": "Company Name",
    "role_summary": "Brief role summary",
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill3"],
    "tech_stack": ["Python", "FastAPI"],
    "experience_years": "3-5 years",
    "education": "Bachelor's Degree",
    "responsibilities": ["responsibility1", "responsibility2"],
    "soft_skills": ["communication", "teamwork"],
    "domain": "Backend/AI/Full Stack",
    "industry": "FinTech/SaaS/Healthcare",
    "salary": "15-25 LPA",
    "location": "Bangalore/Remote",
    "employment_type": "Full-Time",
    "seniority_level": "Senior"
}}"""


ai_service = AIService()
