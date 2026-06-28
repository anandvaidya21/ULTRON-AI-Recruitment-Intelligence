"""
ULTRON AI – Resume Parser Service
Extracts structured candidate profile from raw resume text.
Uses AI (Gemini/OpenAI) when available, falls back to rule-based NLP.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional

from utils.helpers import (
    extract_email, extract_phone, extract_urls,
    extract_years_of_experience, detect_career_level,
    safe_json_load, clean_text
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Known skill keywords for rule-based extraction
# ------------------------------------------------------------------
SKILL_KEYWORDS = [
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby",
    "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "shell",
    # Web
    "html", "css", "react", "vue", "angular", "nextjs", "nuxt", "svelte",
    "fastapi", "django", "flask", "express", "nodejs", "spring", "laravel",
    # Data / AI / ML
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy",
    "machine learning", "deep learning", "nlp", "computer vision", "llm",
    "transformers", "huggingface", "langchain", "openai", "gemini",
    "data science", "data analysis", "data engineering",
    # DevOps / Cloud
    "docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ansible",
    "ci/cd", "jenkins", "github actions", "linux", "devops",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "sqlite", "cassandra", "dynamodb", "supabase", "firebase",
    # Tools
    "git", "github", "jira", "figma", "postman", "graphql", "rest api",
    "microservices", "kafka", "rabbitmq", "nginx",
]

SECTION_HEADERS = {
    "experience": ["experience", "work experience", "employment", "work history", "professional experience"],
    "education": ["education", "academic", "qualification", "degree"],
    "skills": ["skills", "technical skills", "competencies", "expertise", "technologies"],
    "projects": ["projects", "personal projects", "key projects", "notable projects"],
    "certifications": ["certifications", "certificates", "courses", "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
    "hackathons": ["hackathons", "competitions", "contests"],
}


class ResumeParser:
    """
    Parses raw resume text into a structured candidate profile.
    Tries AI parsing first (if ai_service is injected), then falls back to rule-based.
    """

    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def parse(self, raw_text: str, filename: str = "") -> Dict[str, Any]:
        """Main entry point – returns a structured candidate profile dict."""
        if not raw_text or not raw_text.strip():
            return self._empty_profile()

        # Try AI parsing first
        if self.ai_service:
            try:
                profile = self.ai_service.parse_resume(raw_text)
                if profile and profile.get("name"):
                    logger.info("Resume parsed via AI service.")
                    profile = self._enrich_with_rules(profile, raw_text)
                    return profile
            except Exception as e:
                logger.warning(f"AI resume parsing failed: {e}. Falling back to rule-based.")

        # Fallback: rule-based parsing
        return self._rule_based_parse(raw_text)

    def _rule_based_parse(self, text: str) -> Dict[str, Any]:
        """Rule-based resume parsing."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        profile = self._empty_profile()

        # Basic contact info
        profile["email"] = extract_email(text)
        profile["phone"] = extract_phone(text)
        urls = extract_urls(text)
        profile["github_url"] = urls.get("github")
        profile["linkedin_url"] = urls.get("linkedin")
        profile["portfolio_url"] = urls.get("portfolio")

        # Name: usually first non-empty line (heuristic)
        for line in lines[:5]:
            if self._is_likely_name(line):
                profile["name"] = line
                break
        if not profile["name"]:
            profile["name"] = "Unknown Candidate"

        # Skills
        profile["skills"] = self._extract_skills(text)
        profile["technical_skills"] = [s for s in profile["skills"]
                                        if s.lower() in SKILL_KEYWORDS]

        # Sections
        sections = self._split_sections(text)

        # Experience
        exp_text = sections.get("experience", "")
        profile["experience"] = self._parse_experience(exp_text)

        # Education
        edu_text = sections.get("education", "")
        profile["education"] = self._parse_education(edu_text)

        # Projects
        proj_text = sections.get("projects", "")
        profile["projects"] = self._parse_projects(proj_text)

        # Certifications
        cert_text = sections.get("certifications", "")
        profile["certifications"] = self._parse_list_items(cert_text)

        # Achievements
        ach_text = sections.get("achievements", "")
        profile["achievements"] = self._parse_list_items(ach_text)

        # Hackathons
        hack_text = sections.get("hackathons", "")
        profile["hackathons"] = self._parse_list_items(hack_text)

        # Experience years
        profile["total_experience_years"] = extract_years_of_experience(text)
        if not profile["total_experience_years"] and profile["experience"]:
            profile["total_experience_years"] = float(len(profile["experience"]))

        # Career level
        current_role = profile["experience"][0].get("role") if profile["experience"] else None
        profile["current_role"] = current_role
        profile["career_level"] = detect_career_level(
            profile["total_experience_years"], current_role
        )

        # Flags
        profile["open_source"] = bool(profile.get("github_url"))
        profile["deployment_experience"] = any(
            kw in text.lower() for kw in ["deploy", "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd"]
        )

        # Summary
        profile["summary"] = self._extract_summary(text, lines)
        profile["languages"] = self._extract_languages(text)
        profile["industry_domains"] = self._detect_domains(text, profile["skills"])

        return profile

    def _enrich_with_rules(self, profile: Dict, raw_text: str) -> Dict:
        """Enrich AI-parsed profile with rule-based extractions."""
        if not profile.get("github_url"):
            urls = extract_urls(raw_text)
            profile["github_url"] = urls.get("github")
            profile["linkedin_url"] = urls.get("linkedin")
            profile["portfolio_url"] = urls.get("portfolio")

        if not profile.get("email"):
            profile["email"] = extract_email(raw_text)
        if not profile.get("phone"):
            profile["phone"] = extract_phone(raw_text)
        if not profile.get("open_source"):
            profile["open_source"] = bool(profile.get("github_url"))
        if not profile.get("deployment_experience"):
            profile["deployment_experience"] = any(
                kw in raw_text.lower()
                for kw in ["deploy", "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd"]
            )
        return profile

    # ------------------------------------------------------------------
    # Section Parsing Helpers
    # ------------------------------------------------------------------

    def _split_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into named sections."""
        sections: Dict[str, str] = {}
        current_section = "intro"
        current_text: List[str] = []
        lines = text.split('\n')

        for line in lines:
            line_lower = line.strip().lower()
            matched = False
            for section_name, keywords in SECTION_HEADERS.items():
                if any(line_lower.startswith(kw) or line_lower == kw for kw in keywords):
                    if current_text:
                        sections[current_section] = '\n'.join(current_text)
                    current_section = section_name
                    current_text = []
                    matched = True
                    break
            if not matched:
                current_text.append(line)

        if current_text:
            sections[current_section] = '\n'.join(current_text)

        return sections

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching."""
        text_lower = text.lower()
        found = []
        for skill in SKILL_KEYWORDS:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found.append(skill.title() if len(skill.split()) == 1 else skill)
        return list(set(found))

    def _parse_experience(self, text: str) -> List[Dict[str, Any]]:
        """Parse experience section into structured entries."""
        experiences = []
        if not text.strip():
            return experiences

        # Split by common date patterns or double newlines
        entries = re.split(r'\n{2,}', text.strip())
        for entry in entries[:10]:  # max 10 entries
            if len(entry.strip()) < 10:
                continue
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            exp = {
                "role": lines[0] if lines else "Unknown Role",
                "company": lines[1] if len(lines) > 1 else "",
                "duration": self._extract_date_range(entry),
                "description": entry[:300],
                "technologies": self._extract_skills(entry),
            }
            experiences.append(exp)

        return experiences

    def _parse_education(self, text: str) -> List[Dict[str, Any]]:
        """Parse education section."""
        educations = []
        if not text.strip():
            return educations

        entries = re.split(r'\n{2,}', text.strip())
        for entry in entries[:5]:
            if len(entry.strip()) < 5:
                continue
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            degree_keywords = ["b.tech", "b.e", "m.tech", "bsc", "msc", "mba", "phd",
                               "bachelor", "master", "doctorate", "diploma", "b.com", "bca", "mca"]
            degree_line = lines[0] if lines else ""
            edu = {
                "degree": degree_line,
                "institution": lines[1] if len(lines) > 1 else "",
                "year": self._extract_year(entry),
                "grade": self._extract_grade(entry),
                "field": self._extract_field(degree_line),
            }
            educations.append(edu)

        return educations

    def _parse_projects(self, text: str) -> List[Dict[str, Any]]:
        """Parse projects section."""
        projects = []
        if not text.strip():
            return projects

        entries = re.split(r'\n{2,}|\n(?=[A-Z])', text.strip())
        for entry in entries[:10]:
            if len(entry.strip()) < 10:
                continue
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            proj = {
                "name": lines[0] if lines else "Project",
                "description": entry[:400],
                "technologies": self._extract_skills(entry),
                "url": extract_urls(entry).get("github") or extract_urls(entry).get("portfolio"),
            }
            projects.append(proj)

        return projects

    def _parse_list_items(self, text: str) -> List[str]:
        """Parse bullet-point lists into string items."""
        if not text.strip():
            return []
        items = []
        for line in text.split('\n'):
            line = re.sub(r'^[•\-\*\>\◦\▪\▸]\s*', '', line.strip())
            if line and len(line) > 3:
                items.append(line)
        return items[:20]

    def _extract_date_range(self, text: str) -> str:
        """Extract date range like '2020-2022' or 'Jan 2021 - Dec 2022'."""
        pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)?\s*\d{4}\s*[-–—to]+\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current|Now|January|February|March|April|June|July|August|September|October|November|December)?\s*\d{0,4}'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0).strip() if match else ""

    def _extract_year(self, text: str) -> Optional[str]:
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return match.group(0) if match else None

    def _extract_grade(self, text: str) -> Optional[str]:
        patterns = [r'\b(\d+\.\d+)\s*(?:CGPA|GPA|cgpa|gpa)', r'(\d+)%\s*(?:marks|aggregate|score)?']
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0)
        return None

    def _extract_field(self, degree_text: str) -> str:
        fields = {
            "computer": "Computer Science", "cse": "Computer Science",
            "information": "Information Technology", "it": "Information Technology",
            "electrical": "Electrical Engineering", "ece": "Electronics",
            "mechanical": "Mechanical Engineering", "civil": "Civil Engineering",
            "data": "Data Science", "ai": "Artificial Intelligence",
            "math": "Mathematics", "physics": "Physics", "commerce": "Commerce",
        }
        text_lower = degree_text.lower()
        for key, value in fields.items():
            if key in text_lower:
                return value
        return "Engineering"

    def _extract_summary(self, text: str, lines: List[str]) -> str:
        """Extract or generate a brief professional summary."""
        summary_keywords = ["summary", "objective", "profile", "about", "overview"]
        for i, line in enumerate(lines[:10]):
            if any(kw in line.lower() for kw in summary_keywords):
                summary_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    if len(lines[j]) > 20:
                        summary_lines.append(lines[j])
                if summary_lines:
                    return " ".join(summary_lines)
        # Use first substantial paragraph as summary
        for line in lines:
            if len(line) > 80:
                return line[:300]
        return ""

    def _extract_languages(self, text: str) -> List[str]:
        """Extract spoken/human languages."""
        known = ["english", "hindi", "tamil", "telugu", "kannada", "marathi",
                 "bengali", "gujarati", "punjabi", "french", "german", "spanish",
                 "japanese", "chinese", "arabic", "portuguese"]
        text_lower = text.lower()
        return [lang.title() for lang in known if lang in text_lower]

    def _detect_domains(self, text: str, skills: List[str]) -> List[str]:
        """Detect industry domains from text."""
        domains = []
        text_lower = text.lower()
        domain_map = {
            "fintech": ["fintech", "banking", "finance", "payment", "blockchain"],
            "healthtech": ["health", "medical", "clinical", "pharma", "biotech"],
            "edtech": ["edtech", "education", "e-learning", "lms"],
            "ecommerce": ["ecommerce", "e-commerce", "retail", "marketplace"],
            "ai/ml": ["machine learning", "deep learning", "nlp", "ai", "ml"],
            "devops": ["devops", "sre", "platform engineering", "cloud"],
            "data engineering": ["data pipeline", "etl", "data warehouse", "spark"],
            "cybersecurity": ["security", "penetration", "vulnerability", "soc"],
        }
        for domain, keywords in domain_map.items():
            if any(kw in text_lower for kw in keywords):
                domains.append(domain)
        return domains[:4]

    def _is_likely_name(self, line: str) -> bool:
        """Heuristic check if a line looks like a person's name."""
        words = line.split()
        if not (1 < len(words) < 5):
            return False
        # Names are typically title case, not too long, no digits
        if any(char.isdigit() for char in line):
            return False
        if any(char in line for char in ['@', '.com', '/', 'http']):
            return False
        if len(line) > 50:
            return False
        return all(w[0].isupper() for w in words if w)

    def _empty_profile(self) -> Dict[str, Any]:
        """Return an empty candidate profile template."""
        return {
            "name": "Unknown Candidate",
            "email": None,
            "phone": None,
            "location": None,
            "summary": "",
            "skills": [],
            "technical_skills": [],
            "soft_skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "hackathons": [],
            "achievements": [],
            "languages": [],
            "github_url": None,
            "linkedin_url": None,
            "portfolio_url": None,
            "total_experience_years": 0.0,
            "current_role": None,
            "career_level": "Junior",
            "industry_domains": [],
            "open_source": False,
            "deployment_experience": False,
        }
