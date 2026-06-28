"""
ULTRON AI – Job Description Analyzer
Parses and understands job descriptions semantically.
Extracts structured requirements beyond simple keyword lists.
"""

import re
import logging
from typing import Dict, Any, List, Optional

from utils.helpers import clean_text, safe_json_load

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """
    Analyzes job descriptions to extract:
    - Required and preferred skills
    - Experience requirements
    - Education requirements
    - Domain & industry context
    - Soft skill requirements
    - Hidden requirements
    """

    EXPERIENCE_PATTERNS = [
        r'(\d+)\+?\s*[-–]?\s*(\d+)?\s*years?\s+(?:of\s+)?experience',
        r'minimum\s+(\d+)\s+years?',
        r'at\s+least\s+(\d+)\s+years?',
        r'(\d+)\s+to\s+(\d+)\s+years?',
    ]

    EDUCATION_KEYWORDS = {
        "bachelor": "Bachelor's Degree",
        "b.tech": "B.Tech",
        "b.e": "B.E",
        "master": "Master's Degree",
        "m.tech": "M.Tech",
        "mba": "MBA",
        "phd": "PhD",
        "doctorate": "Doctorate",
        "diploma": "Diploma",
    }

    SOFT_SKILLS = [
        "communication", "teamwork", "leadership", "problem-solving",
        "critical thinking", "adaptability", "creativity", "time management",
        "collaboration", "analytical", "attention to detail", "ownership",
        "proactive", "self-motivated", "interpersonal", "presentation",
        "mentoring", "stakeholder management",
    ]

    EMPLOYMENT_TYPES = {
        "full-time": "Full-Time",
        "full time": "Full-Time",
        "part-time": "Part-Time",
        "contract": "Contract",
        "internship": "Internship",
        "remote": "Remote",
        "hybrid": "Hybrid",
        "on-site": "On-Site",
        "onsite": "On-Site",
        "freelance": "Freelance",
    }

    TECH_KEYWORDS = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "kotlin",
        "react", "vue", "angular", "nextjs", "fastapi", "django", "flask", "express",
        "nodejs", "spring", "tensorflow", "pytorch", "scikit-learn", "nlp", "llm",
        "docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ci/cd",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "git", "microservices", "rest", "graphql", "kafka", "spark",
        "machine learning", "deep learning", "data science", "computer vision",
        "pandas", "numpy", "langchain", "openai", "gemini", "huggingface",
        "html", "css", "tailwind", "sass", "webpack", "vite",
        "linux", "bash", "jenkins", "github actions", "ansible",
    ]

    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def analyze(self, raw_description: str, title: str = "", company: str = "") -> Dict[str, Any]:
        """Analyze a job description and return structured data."""
        if not raw_description.strip():
            return self._empty_jd(title, company)

        # Try AI analysis first
        if self.ai_service:
            try:
                parsed = self.ai_service.analyze_job_description(raw_description)
                if parsed and isinstance(parsed, dict):
                    logger.info("JD analyzed via AI service.")
                    parsed = self._enrich_jd(parsed, raw_description, title, company)
                    return parsed
            except Exception as e:
                logger.warning(f"AI JD analysis failed: {e}. Using rule-based parser.")

        # Fallback: rule-based parsing
        return self._rule_based_analyze(raw_description, title, company)

    def _rule_based_analyze(self, text: str, title: str, company: str) -> Dict[str, Any]:
        """Rule-based job description analysis."""
        text_lower = text.lower()

        jd = self._empty_jd(title, company)

        # Title (from param or first line)
        if not jd["title"]:
            first_line = text.strip().split('\n')[0].strip()
            if len(first_line) < 100:
                jd["title"] = first_line
            else:
                jd["title"] = "Software Engineer"

        # Company
        company_match = re.search(r'(?:at|@|company[:\s]+)([A-Z][A-Za-z\s&,.]+?)(?:\n|,|\.|–|-)', text)
        if company_match and not jd["company"]:
            jd["company"] = company_match.group(1).strip()

        # Experience
        jd["experience_years"] = self._extract_experience(text)

        # Education
        jd["education"] = self._extract_education(text_lower)

        # Skills
        jd["required_skills"] = self._extract_skills(text, required=True)
        jd["preferred_skills"] = self._extract_skills(text, required=False)
        jd["tech_stack"] = self._extract_tech_stack(text_lower)

        # Soft skills
        jd["soft_skills"] = [s for s in self.SOFT_SKILLS if s in text_lower]

        # Responsibilities
        jd["responsibilities"] = self._extract_responsibilities(text)

        # Employment type
        for key, val in self.EMPLOYMENT_TYPES.items():
            if key in text_lower:
                jd["employment_type"] = val
                break

        # Location
        jd["location"] = self._extract_location(text)

        # Salary
        jd["salary"] = self._extract_salary(text)

        # Domain & Industry
        jd["domain"] = self._detect_domain(text_lower)
        jd["industry"] = self._detect_industry(text_lower)

        # Seniority
        jd["seniority_level"] = self._detect_seniority(text_lower, title)

        # Role summary
        jd["role_summary"] = self._extract_role_summary(text)

        return jd

    def _enrich_jd(self, parsed: Dict, raw: str, title: str, company: str) -> Dict:
        """Enrich AI-parsed JD with rule-based fields."""
        text_lower = raw.lower()
        if not parsed.get("tech_stack"):
            parsed["tech_stack"] = self._extract_tech_stack(text_lower)
        if not parsed.get("domain"):
            parsed["domain"] = self._detect_domain(text_lower)
        if not parsed.get("industry"):
            parsed["industry"] = self._detect_industry(text_lower)
        if not parsed.get("seniority_level"):
            parsed["seniority_level"] = self._detect_seniority(text_lower, title)
        if title and not parsed.get("title"):
            parsed["title"] = title
        if company and not parsed.get("company"):
            parsed["company"] = company
        return parsed

    def _extract_experience(self, text: str) -> str:
        """Extract experience requirement."""
        for pattern in self.EXPERIENCE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "Not specified"

    def _extract_education(self, text_lower: str) -> str:
        """Extract education requirement."""
        for key, val in self.EDUCATION_KEYWORDS.items():
            if key in text_lower:
                return val
        return "Not specified"

    def _extract_skills(self, text: str, required: bool) -> List[str]:
        """Extract required or preferred skills."""
        skills = []
        lines = text.split('\n')

        required_section = False
        preferred_section = False

        for line in lines:
            line_lower = line.lower().strip()
            if any(kw in line_lower for kw in ["required", "must have", "essential", "mandatory"]):
                required_section = True
                preferred_section = False
            elif any(kw in line_lower for kw in ["preferred", "nice to have", "good to have", "bonus", "plus"]):
                preferred_section = True
                required_section = False

            for tech in self.TECH_KEYWORDS:
                if re.search(r'\b' + re.escape(tech) + r'\b', line_lower):
                    if required and (required_section or not preferred_section):
                        if tech not in skills:
                            skills.append(tech.title() if len(tech.split()) == 1 else tech)
                    elif not required and preferred_section:
                        if tech not in skills:
                            skills.append(tech.title() if len(tech.split()) == 1 else tech)

        # If no section separation, extract all skills for required
        if required and not skills:
            text_lower = text.lower()
            for tech in self.TECH_KEYWORDS:
                if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
                    skills.append(tech.title() if len(tech.split()) == 1 else tech)

        return list(set(skills))[:20]

    def _extract_tech_stack(self, text_lower: str) -> List[str]:
        """Extract all technology mentions."""
        found = []
        for tech in self.TECH_KEYWORDS:
            if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
                found.append(tech.title() if len(tech.split()) == 1 else tech)
        return list(set(found))[:25]

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities as bullet points."""
        responsibilities = []
        lines = text.split('\n')
        in_resp_section = False

        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()

            if any(kw in line_lower for kw in ["responsibilities", "what you'll do", "your role", "duties", "what you will do"]):
                in_resp_section = True
                continue

            if in_resp_section:
                if any(kw in line_lower for kw in ["requirement", "qualification", "skill", "must have"]):
                    in_resp_section = False
                    continue
                # Bullet points
                clean = re.sub(r'^[•\-\*\>\◦\▪\▸\d\.\)]\s*', '', line_stripped)
                if len(clean) > 15:
                    responsibilities.append(clean)

        return responsibilities[:10]

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location."""
        patterns = [
            r'(?:location|based in|office in|position in)[:\s]+([A-Za-z\s,]+?)(?:\n|\.)',
            r'\b(Bangalore|Mumbai|Delhi|Hyderabad|Chennai|Pune|Kolkata|Gurgaon|Noida|Remote|Hybrid)\b',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1 if '(' in pattern else 0).strip()
        return None

    def _extract_salary(self, text: str) -> Optional[str]:
        """Extract salary/CTC information."""
        patterns = [
            r'(?:salary|ctc|compensation|package)[:\s]+([₹$]?\d+[\d,\.]*\s*(?:LPA|lpa|lakhs?|K|k|USD|INR)?(?:\s*[-–]\s*[₹$]?\d+[\d,\.]*\s*(?:LPA|lpa|lakhs?|K|k)?)?)',
            r'([₹$]\s*\d+[\d,\.]*\s*(?:LPA|K)?(?:\s*[-–]\s*[₹$]?\d+[\d,\.]*\s*(?:LPA|K)?)?)',
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _detect_domain(self, text_lower: str) -> str:
        """Detect primary domain."""
        domains = {
            "AI/ML": ["machine learning", "deep learning", "llm", "nlp", "computer vision", "ai "],
            "Data Engineering": ["data pipeline", "etl", "data warehouse", "big data", "spark"],
            "Backend": ["backend", "api", "server", "microservices", "database"],
            "Frontend": ["frontend", "ui", "react", "vue", "angular", "web development"],
            "Full Stack": ["full stack", "fullstack", "full-stack"],
            "DevOps": ["devops", "cloud", "kubernetes", "ci/cd", "infrastructure"],
            "Mobile": ["android", "ios", "flutter", "react native", "mobile"],
            "Data Science": ["data science", "data analyst", "analytics", "statistics"],
            "Security": ["security", "penetration", "cybersecurity", "soc"],
        }
        for domain, keywords in domains.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        return "Software Engineering"

    def _detect_industry(self, text_lower: str) -> str:
        """Detect industry vertical."""
        industries = {
            "FinTech": ["fintech", "banking", "payment", "financial", "insurance"],
            "HealthTech": ["health", "medical", "clinical", "pharma", "hospital"],
            "EdTech": ["edtech", "education", "learning", "lms"],
            "E-Commerce": ["ecommerce", "retail", "marketplace", "shopping"],
            "SaaS": ["saas", "software as a service", "platform", "b2b"],
            "Startup": ["startup", "seed", "series a", "venture"],
            "Enterprise": ["enterprise", "fortune 500", "large scale", "global"],
        }
        for industry, keywords in industries.items():
            if any(kw in text_lower for kw in keywords):
                return industry
        return "Technology"

    def _detect_seniority(self, text_lower: str, title: str) -> str:
        """Detect seniority level."""
        title_lower = title.lower()
        combined = text_lower + " " + title_lower

        if any(w in combined for w in ["intern", "fresher", "entry level", "0-1 year"]):
            return "Intern/Entry"
        if any(w in combined for w in ["junior", "associate", "1-2 year"]):
            return "Junior"
        if any(w in combined for w in ["senior", "sr.", "3+ year", "5+ year"]):
            return "Senior"
        if any(w in combined for w in ["lead", "principal", "staff", "architect"]):
            return "Lead/Principal"
        if any(w in combined for w in ["manager", "director", "vp", "head", "chief"]):
            return "Management"
        return "Mid-level"

    def _extract_role_summary(self, text: str) -> str:
        """Extract a brief role summary from the beginning of the JD."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for para in paragraphs[:3]:
            if len(para) > 80:
                return para[:400]
        return text[:300]

    def _empty_jd(self, title: str, company: str) -> Dict[str, Any]:
        """Return empty JD template."""
        return {
            "title": title or "",
            "company": company or "",
            "role_summary": "",
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": "Not specified",
            "education": "Not specified",
            "responsibilities": [],
            "soft_skills": [],
            "domain": "Software Engineering",
            "industry": "Technology",
            "salary": None,
            "location": None,
            "employment_type": "Full-Time",
            "tech_stack": [],
            "seniority_level": "Mid-level",
        }


job_analyzer = JobAnalyzer()
