"""
ULTRON AI – Chat Service
AI Recruiter Assistant – understands natural language queries
about candidates and returns intelligent, context-aware answers.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from services.ai_service import ai_service
from database import crud

logger = logging.getLogger(__name__)


class ChatService:
    """
    Handles AI Recruiter chat interactions.
    Classifies intent, fetches relevant candidates, generates responses.
    """

    INTENTS = {
        "find_skill": ["find", "show", "who has", "candidates with", "good at", "knows", "experienced in"],
        "top_candidates": ["best", "top", "highest", "rank", "recommend", "strongest"],
        "experience_filter": ["experience", "years", "senior", "junior", "fresher", "lead"],
        "culture_fit": ["startup", "culture", "fit", "team", "collaborative"],
        "deployment": ["deploy", "docker", "kubernetes", "cloud", "devops", "aws", "gcp"],
        "education": ["education", "degree", "college", "university", "graduation"],
        "projects": ["project", "portfolio", "github", "open source", "built"],
        "analytics": ["average", "distribution", "how many", "statistics", "count", "total"],
        "greeting": ["hello", "hi", "hey", "help", "what can you"],
    }

    def process_message(self, message: str, session_id: str,
                        db: Session, job_id: Optional[int] = None) -> Dict[str, Any]:
        """Process a recruiter message and return a response."""

        # Save user message
        crud.save_chat_message(db, session_id, "user", message)

        # Detect intent
        intent = self._detect_intent(message)
        logger.info(f"Chat intent: {intent} | message: {message[:50]}")

        # Get context (candidates + job)
        context = self._build_context(db, job_id)

        # Generate response
        response_text, mentioned_candidates, suggestions = self._generate_response(
            message, intent, context, db, job_id
        )

        # Save assistant response
        crud.save_chat_message(db, session_id, "assistant", response_text,
                               chat_metadata={"intent": intent, "mentioned": mentioned_candidates})

        return {
            "response": response_text,
            "candidates_mentioned": mentioned_candidates,
            "session_id": session_id,
            "suggestions": suggestions,
        }

    def _detect_intent(self, message: str) -> str:
        """Classify message intent."""
        message_lower = message.lower()
        for intent, keywords in self.INTENTS.items():
            if any(kw in message_lower for kw in keywords):
                return intent
        return "general"

    def _build_context(self, db: Session, job_id: Optional[int]) -> str:
        """Build context string from database for the LLM."""
        try:
            candidates = crud.get_all_candidates(db, limit=20)
            jobs = crud.get_all_jobs(db, limit=5)

            context_parts = []

            if jobs:
                job = jobs[0]
                context_parts.append(f"Current Job: {job.title} at {job.company or 'Company'}")
                if job.parsed_data:
                    req_skills = job.parsed_data.get("required_skills", [])[:5]
                    context_parts.append(f"Required Skills: {', '.join(req_skills)}")

            context_parts.append(f"\nTotal Candidates in System: {len(candidates)}")

            if candidates:
                top_candidates = []
                for c in candidates[:5]:
                    profile = c.parsed_profile or {}
                    skills = profile.get("skills", [])[:4]
                    exp = profile.get("total_experience_years", 0)
                    top_candidates.append(
                        f"- {c.name}: {exp}y exp, skills: {', '.join(skills[:3])}"
                    )
                context_parts.append("Candidates:\n" + "\n".join(top_candidates))

            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Context build error: {e}")
            return "No candidates data available yet."

    def _generate_response(self, message: str, intent: str, context: str,
                           db: Session, job_id: Optional[int]) -> tuple:
        """Generate response based on intent."""
        mentioned = []
        suggestions = self._get_suggestions(intent)

        # Try to use LLM for response
        if ai_service.get_provider() != "rule_based":
            full_context = (
                f"You are ULTRON AI, an expert AI recruitment assistant.\n"
                f"Context:\n{context}\n\n"
                f"Be concise, helpful, and specific. Reference actual candidates when relevant."
            )
            try:
                response = ai_service.chat(message, full_context)
                mentioned = self._extract_mentioned_candidates(response, db)
                return response, mentioned, suggestions
            except Exception:
                pass

        # Rule-based response with actual data
        response = self._rule_based_response(message, intent, context, db)
        mentioned = self._extract_mentioned_candidates(response, db)
        return response, mentioned, suggestions

    def _rule_based_response(self, message: str, intent: str, context: str,
                              db: Session) -> str:
        """Generate intelligent rule-based response using actual data."""
        candidates = crud.get_all_candidates(db, limit=50)
        msg_lower = message.lower()

        if intent == "greeting":
            return (
                "👋 Hello! I'm **ULTRON AI**, your intelligent recruitment assistant.\n\n"
                f"I currently have **{len(candidates)} candidates** in the system.\n\n"
                "You can ask me:\n"
                "• \"Find candidates good at Python\"\n"
                "• \"Show me senior developers\"\n"
                "• \"Who has deployment experience?\"\n"
                "• \"Which candidates fit startup culture?\"\n"
                "• \"Show top-ranked candidates\""
            )

        elif intent == "find_skill":
            # Extract skill from message
            skill = self._extract_skill_from_message(msg_lower)
            if skill:
                matches = self._find_by_skill(candidates, skill)
                if matches:
                    names = [f"**{m['name']}** ({m['exp']}y exp)" for m in matches[:4]]
                    return (
                        f"🎯 Found **{len(matches)} candidates** with {skill} experience:\n\n"
                        + "\n".join(f"• {n}" for n in names) + "\n\n"
                        "View their full profiles in the Candidates section."
                    )
                else:
                    return (f"I couldn't find candidates specifically mentioning **{skill}**. "
                            "Try checking the Candidates page and filtering by skills. "
                            "Consider uploading more resumes with this skill.")
            else:
                return "Please specify which skill you're looking for. For example: 'Find Python developers'."

        elif intent == "top_candidates":
            analyses = crud.get_all_analyses(db)
            if analyses:
                top = analyses[:3]
                result = "🏆 **Top Ranked Candidates:**\n\n"
                for i, a in enumerate(top):
                    candidate = crud.get_candidate(db, a.candidate_id)
                    if candidate:
                        result += f"{i+1}. **{candidate.name}** — {a.overall_score:.1f}% match\n"
                result += "\nSee full rankings in the Rankings Dashboard."
                return result
            else:
                n = len(candidates)
                return (f"I have **{n} candidates** in the system, but no rankings yet. "
                        "Go to 'Upload Job' first, then run 'Analyze' to generate AI rankings.")

        elif intent == "experience_filter":
            level = "senior" if "senior" in msg_lower else "junior" if "junior" in msg_lower else "mid"
            filtered = []
            for c in candidates:
                profile = c.parsed_profile or {}
                career_level = profile.get("career_level", "").lower()
                if level in career_level or (level == "mid" and "mid" in career_level):
                    filtered.append(c.name)
            if filtered:
                return (f"Found **{len(filtered)} {level}-level candidates**: "
                        + ", ".join(filtered[:5])
                        + ("\n(and more...)" if len(filtered) > 5 else ""))
            else:
                return f"No {level}-level candidates found in the current pool."

        elif intent == "deployment":
            deploy_candidates = [c for c in candidates
                                if c.parsed_profile and c.parsed_profile.get("deployment_experience")]
            if deploy_candidates:
                names = [f"**{c.name}**" for c in deploy_candidates[:4]]
                return (f"🚀 Found **{len(deploy_candidates)} candidates** with deployment experience:\n\n"
                        + "\n".join(f"• {n}" for n in names))
            else:
                return ("No candidates explicitly mentioning deployment experience found. "
                        "Check individual profiles — deployment skills may be listed in projects.")

        elif intent == "culture_fit":
            startup_fits = []
            for c in candidates:
                profile = c.parsed_profile or {}
                score = 0
                if profile.get("github_url"):
                    score += 1
                if profile.get("hackathons"):
                    score += 1
                if profile.get("open_source"):
                    score += 1
                if profile.get("deployment_experience"):
                    score += 1
                if profile.get("projects") and len(profile["projects"]) >= 3:
                    score += 1
                if score >= 2:
                    startup_fits.append((c.name, score))

            startup_fits.sort(key=lambda x: -x[1])
            if startup_fits:
                names = [f"**{n}** (score: {s}/5)" for n, s in startup_fits[:4]]
                return ("🚀 **Best startup culture fits** (based on GitHub, hackathons, projects):\n\n"
                        + "\n".join(f"• {n}" for n in names))
            else:
                return ("Startup culture fit is assessed from GitHub activity, hackathons, and personal projects. "
                        "No strong fits detected yet — consider asking candidates to share these details.")

        elif intent == "analytics":
            total = len(candidates)
            github_count = sum(1 for c in candidates if c.github_url)
            avg_exp = 0
            if candidates:
                exps = [c.parsed_profile.get("total_experience_years", 0) or 0
                        for c in candidates if c.parsed_profile]
                avg_exp = sum(exps) / len(exps) if exps else 0
            return (f"📊 **Candidate Analytics:**\n\n"
                    f"• Total Candidates: **{total}**\n"
                    f"• Average Experience: **{avg_exp:.1f} years**\n"
                    f"• GitHub Profiles: **{github_count}**\n\n"
                    "Visit the Analytics dashboard for detailed visualizations.")

        else:
            return (f"I processed your query: *\"{message}\"*\n\n"
                    f"I have **{len(candidates)} candidates** in the system. "
                    "You can ask me to find candidates by skill, experience, deployment experience, "
                    "GitHub activity, or startup culture fit. What would you like to explore?")

    def _extract_skill_from_message(self, msg: str) -> Optional[str]:
        """Extract skill name from message."""
        skills = [
            "python", "javascript", "typescript", "react", "vue", "angular",
            "fastapi", "django", "flask", "nodejs", "java", "go", "rust",
            "machine learning", "deep learning", "nlp", "ai", "ml",
            "docker", "kubernetes", "aws", "gcp", "azure",
            "sql", "mongodb", "postgresql", "redis",
            "tensorflow", "pytorch", "langchain", "llm",
            "data science", "data engineering", "devops",
        ]
        for skill in skills:
            if skill in msg:
                return skill.title() if len(skill.split()) == 1 else skill
        return None

    def _find_by_skill(self, candidates, skill: str) -> List[Dict]:
        """Find candidates with a specific skill."""
        skill_lower = skill.lower()
        matches = []
        for c in candidates:
            profile = c.parsed_profile or {}
            all_skills = [s.lower() for s in profile.get("skills", []) + profile.get("technical_skills", [])]
            if any(skill_lower in s or s in skill_lower for s in all_skills):
                matches.append({
                    "id": c.id,
                    "name": c.name,
                    "exp": profile.get("total_experience_years", 0) or 0
                })
        return matches

    def _extract_mentioned_candidates(self, response: str, db: Session) -> List[int]:
        """Extract candidate IDs mentioned in the response."""
        candidates = crud.get_all_candidates(db, limit=50)
        mentioned = []
        for c in candidates:
            if c.name and c.name in response:
                mentioned.append(c.id)
        return mentioned[:3]

    def _get_suggestions(self, intent: str) -> List[str]:
        """Return follow-up suggestions based on intent."""
        suggestions_map = {
            "find_skill": ["Find Python developers", "Show React candidates", "Who knows Docker?"],
            "top_candidates": ["Show skills breakdown", "Filter by experience", "Download top 5 profiles"],
            "greeting": ["Find top candidates", "Show deployment experts", "Who fits startup culture?"],
            "general": ["Show top candidates", "Find by skill", "View Analytics"],
        }
        return suggestions_map.get(intent, ["Show top candidates", "View Rankings", "View Analytics"])


chat_service = ChatService()
