"""
ULTRON AI – Semantic Matching Engine
Compares a job description against candidate profiles using vector similarity.
Generates multi-dimensional match scores across 8 key dimensions.
"""

import numpy as np
import logging
import re
from typing import Dict, Any, Optional, List

from services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Multi-dimensional semantic matching between job and candidate.
    Each dimension is scored independently and then combined.
    """

    # Dimension weights (sum to 1.0)
    WEIGHTS = {
        "skills":      0.25,
        "experience":  0.20,
        "projects":    0.15,
        "education":   0.10,
        "industry":    0.10,
        "soft_skills": 0.08,
        "growth":      0.07,
        "github":      0.05,
    }

    def match(self, job_data: Dict, candidate_data: Dict,
              job_embedding: Optional[np.ndarray] = None,
              candidate_embedding: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Compute multi-dimensional match scores.
        Returns a dict with individual dimension scores and overall score.
        """
        scores = {}

        # 1. Overall semantic similarity (embedding-based)
        semantic_sim = 0.0
        if job_embedding is not None and candidate_embedding is not None:
            semantic_sim = embedding_service.cosine_similarity(job_embedding, candidate_embedding)

        # 2. Skills Match
        scores["skills"] = self._match_skills(job_data, candidate_data, semantic_sim)

        # 3. Experience Match
        scores["experience"] = self._match_experience(job_data, candidate_data)

        # 4. Projects Match
        scores["projects"] = self._match_projects(job_data, candidate_data, semantic_sim)

        # 5. Education Match
        scores["education"] = self._match_education(job_data, candidate_data)

        # 6. Industry Match
        scores["industry"] = self._match_industry(job_data, candidate_data)

        # 7. Soft Skills Match
        scores["soft_skills"] = self._match_soft_skills(job_data, candidate_data, semantic_sim)

        # 8. Growth Match (career progression)
        scores["growth"] = self._match_growth(job_data, candidate_data)

        # 9. GitHub/Portfolio bonus
        scores["github"] = self._score_github(candidate_data)
        scores["portfolio"] = self._score_portfolio(candidate_data)
        scores["certifications"] = self._score_certifications(candidate_data)

        # Semantic similarity stored separately
        scores["semantic_similarity"] = round(semantic_sim * 100, 2)

        # Weighted overall score
        weighted_sum = 0.0
        for dim, weight in self.WEIGHTS.items():
            weighted_sum += scores.get(dim, 0) * weight

        # Boost for github/portfolio/certs
        bonus = (scores["github"] * 0.02 + scores["portfolio"] * 0.01 +
                 scores["certifications"] * 0.01)

        # Blend semantic similarity (30%) with weighted score (70%)
        final_score = (weighted_sum * 0.7 + semantic_sim * 100 * 0.3) + bonus
        scores["overall"] = round(min(100.0, final_score), 2)

        # Round all scores to 2 decimal places
        for key in scores:
            scores[key] = round(scores[key], 2)

        return scores

    # ------------------------------------------------------------------
    # Dimension Matchers
    # ------------------------------------------------------------------

    def _match_skills(self, job: Dict, candidate: Dict, semantic_sim: float) -> float:
        """
        Compare required skills against candidate skills.
        Uses both exact matching and semantic similarity boost.
        """
        required = [s.lower() for s in job.get("required_skills", [])]
        preferred = [s.lower() for s in job.get("preferred_skills", [])]
        tech_stack = [s.lower() for s in job.get("tech_stack", [])]

        all_job_skills = list(set(required + preferred + tech_stack))
        candidate_skills = [s.lower() for s in candidate.get("skills", []) +
                           candidate.get("technical_skills", [])]

        if not all_job_skills:
            return 50.0 + semantic_sim * 30  # Use semantic similarity

        # Count matches
        required_matches = sum(1 for s in required if any(
            self._skill_match(s, cs) for cs in candidate_skills))
        preferred_matches = sum(1 for s in preferred if any(
            self._skill_match(s, cs) for cs in candidate_skills))
        stack_matches = sum(1 for s in tech_stack if any(
            self._skill_match(s, cs) for cs in candidate_skills))

        # Score calculation
        req_score = (required_matches / max(len(required), 1)) * 100 if required else 70
        pref_score = (preferred_matches / max(len(preferred), 1)) * 100 if preferred else 50
        stack_score = (stack_matches / max(len(tech_stack), 1)) * 100 if tech_stack else 50

        # Weighted: required > tech_stack > preferred
        base_score = req_score * 0.5 + stack_score * 0.3 + pref_score * 0.2

        # Semantic boost
        final = base_score * 0.75 + semantic_sim * 100 * 0.25
        return min(100.0, final)

    def _skill_match(self, job_skill: str, candidate_skill: str) -> bool:
        """Check if two skills match (including partial/alias matching)."""
        if job_skill == candidate_skill:
            return True
        if job_skill in candidate_skill or candidate_skill in job_skill:
            return True
        # Common aliases
        aliases = {
            "ml": "machine learning", "ai": "artificial intelligence",
            "js": "javascript", "ts": "typescript", "py": "python",
            "k8s": "kubernetes", "pg": "postgresql", "mongo": "mongodb",
        }
        job_alias = aliases.get(job_skill, job_skill)
        cand_alias = aliases.get(candidate_skill, candidate_skill)
        return job_alias == cand_alias

    def _match_experience(self, job: Dict, candidate: Dict) -> float:
        """Match experience requirements."""
        required_exp_str = job.get("experience_years", "")
        candidate_years = candidate.get("total_experience_years", 0) or 0
        seniority_level = job.get("seniority_level", "Mid-level").lower()

        # Parse required years
        required_years = self._parse_experience_requirement(required_exp_str, seniority_level)

        if required_years == 0:
            return 70.0  # Unknown requirement

        if candidate_years == 0:
            # Check career level
            career_level = candidate.get("career_level", "").lower()
            if "intern" in career_level or "junior" in career_level:
                candidate_years = 1.0
            elif "mid" in career_level:
                candidate_years = 3.0
            elif "senior" in career_level:
                candidate_years = 6.0
            else:
                candidate_years = 2.0

        ratio = candidate_years / required_years

        if ratio >= 1.5:
            return 85.0   # Overqualified (slight penalty)
        elif ratio >= 1.0:
            return 100.0  # Perfect match
        elif ratio >= 0.8:
            return 85.0   # Slightly under
        elif ratio >= 0.5:
            return 60.0   # Needs growth
        else:
            return 30.0   # Significantly under

    def _parse_experience_requirement(self, exp_str: str, seniority: str) -> float:
        """Extract numeric years from experience requirement string."""
        if not exp_str:
            # Infer from seniority
            seniority_map = {
                "intern": 0, "junior": 1, "entry": 1, "mid-level": 3,
                "senior": 5, "lead": 7, "principal": 8, "management": 8
            }
            for key, years in seniority_map.items():
                if key in seniority:
                    return float(years)
            return 3.0

        numbers = re.findall(r'\d+', exp_str)
        if numbers:
            return float(numbers[0])
        return 3.0

    def _match_projects(self, job: Dict, candidate: Dict, semantic_sim: float) -> float:
        """Match project relevance."""
        job_tech = [s.lower() for s in job.get("tech_stack", []) + job.get("required_skills", [])]
        candidate_projects = candidate.get("projects", [])

        if not candidate_projects:
            return 30.0 + semantic_sim * 20

        # Check if projects use relevant technologies
        relevant_count = 0
        for project in candidate_projects:
            project_techs = [t.lower() for t in project.get("technologies", [])]
            project_desc = project.get("description", "").lower()
            if any(tech in project_desc or tech in project_techs for tech in job_tech):
                relevant_count += 1

        relevance_ratio = relevant_count / len(candidate_projects)
        project_count_bonus = min(20, len(candidate_projects) * 3)  # Up to 20 points

        score = relevance_ratio * 70 + project_count_bonus + semantic_sim * 10
        return min(100.0, score)

    def _match_education(self, job: Dict, candidate: Dict) -> float:
        """Match education requirements."""
        required_edu = job.get("education", "").lower()
        candidate_education = candidate.get("education", [])

        if not required_edu or required_edu == "not specified":
            return 70.0  # No specific requirement

        # Check if candidate meets education requirement
        edu_level_score = 50.0
        for edu in candidate_education:
            degree = edu.get("degree", "").lower()
            if "phd" in required_edu or "doctorate" in required_edu:
                if "phd" in degree or "doctorate" in degree:
                    edu_level_score = 100.0
                elif "master" in degree or "m.tech" in degree:
                    edu_level_score = 80.0
            elif "master" in required_edu or "m.tech" in required_edu:
                if "phd" in degree or "master" in degree or "m.tech" in degree:
                    edu_level_score = 100.0
                elif "bachelor" in degree or "b.tech" in degree:
                    edu_level_score = 70.0
            elif "bachelor" in required_edu or "b.tech" in required_edu or "b.e" in required_edu:
                if any(kw in degree for kw in ["bachelor", "b.tech", "b.e", "b.sc", "bca"]):
                    edu_level_score = 100.0
                else:
                    edu_level_score = 60.0

        # Bonus for relevant field
        job_domain = job.get("domain", "").lower()
        for edu in candidate_education:
            field = edu.get("field", "").lower()
            if "computer" in field or "information" in field or "data" in field:
                edu_level_score = min(100, edu_level_score + 10)

        return edu_level_score

    def _match_industry(self, job: Dict, candidate: Dict) -> float:
        """Match industry/domain experience."""
        job_industry = job.get("industry", "").lower()
        job_domain = job.get("domain", "").lower()
        candidate_domains = [d.lower() for d in candidate.get("industry_domains", [])]

        if not candidate_domains:
            return 40.0

        # Direct industry match
        if any(job_industry in d or d in job_industry for d in candidate_domains):
            return 100.0
        if any(job_domain in d or d in job_domain for d in candidate_domains):
            return 85.0

        # Partial match
        related = {
            "ai/ml": ["data science", "data engineering", "nlp"],
            "fintech": ["banking", "saas"],
            "saas": ["enterprise", "startup"],
        }
        for key, related_list in related.items():
            if key in job_industry or key in job_domain:
                if any(r in str(candidate_domains) for r in related_list):
                    return 70.0

        return 40.0

    def _match_soft_skills(self, job: Dict, candidate: Dict, semantic_sim: float) -> float:
        """Match soft skills."""
        job_soft = [s.lower() for s in job.get("soft_skills", [])]
        candidate_text = " ".join([
            candidate.get("summary", ""),
            " ".join([p.get("description", "") for p in candidate.get("projects", [])])
        ]).lower()

        if not job_soft:
            return 60.0 + semantic_sim * 20

        matched = sum(1 for skill in job_soft if skill in candidate_text)
        ratio = matched / len(job_soft)
        return 40.0 + ratio * 40 + semantic_sim * 20

    def _match_growth(self, job: Dict, candidate: Dict) -> float:
        """Assess candidate growth trajectory."""
        experience_entries = candidate.get("experience", [])
        years = candidate.get("total_experience_years", 0) or 0
        has_progression = len(experience_entries) > 1

        score = 50.0

        # More jobs = more progression evidence
        if len(experience_entries) >= 3:
            score += 20
        elif len(experience_entries) >= 2:
            score += 10

        # Open source & deployment
        if candidate.get("open_source"):
            score += 10
        if candidate.get("deployment_experience"):
            score += 10

        # Hackathons and certifications
        if candidate.get("hackathons"):
            score += 5
        if candidate.get("certifications"):
            score += 5

        return min(100.0, score)

    def _score_github(self, candidate: Dict) -> float:
        """Score GitHub presence."""
        if candidate.get("github_url"):
            return 100.0
        if candidate.get("open_source"):
            return 70.0
        return 0.0

    def _score_portfolio(self, candidate: Dict) -> float:
        """Score portfolio presence."""
        if candidate.get("portfolio_url"):
            return 100.0
        if candidate.get("projects") and len(candidate.get("projects", [])) >= 3:
            return 50.0
        return 0.0

    def _score_certifications(self, candidate: Dict) -> float:
        """Score certifications."""
        certs = candidate.get("certifications", [])
        if len(certs) >= 3:
            return 100.0
        elif len(certs) >= 1:
            return 60.0
        return 0.0


matching_engine = MatchingEngine()
