"""
ULTRON AI – Explainable Scoring Engine
Generates weighted scores AND human-readable explanations for every candidate.
Never outputs only numbers – always provides reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Takes matching scores and generates:
    - Final weighted score
    - Strengths list
    - Weaknesses list
    - Missing skills
    - Why ranked here
    - Interview recommendation
    - Hiring recommendation
    - Risk analysis
    - Confidence score
    """

    # Tier thresholds
    EXCELLENT  = 80
    GOOD       = 65
    AVERAGE    = 50
    POOR       = 35

    def generate_report(self, job_data: Dict, candidate_data: Dict,
                        scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate a complete explainability report for a candidate.
        """
        overall = scores.get("overall", 0)
        name = candidate_data.get("name", "Candidate")
        job_title = job_data.get("title", "this role")

        # Strengths
        strengths = self._identify_strengths(job_data, candidate_data, scores)

        # Weaknesses
        weaknesses = self._identify_weaknesses(job_data, candidate_data, scores)

        # Missing skills
        missing_skills = self._find_missing_skills(job_data, candidate_data)

        # Ranking reason
        why_ranked = self._explain_ranking(overall, scores, job_title, name)

        # Recommendations
        interview_rec = self._interview_recommendation(overall, scores, name)
        hiring_rec    = self._hiring_recommendation(overall, scores, name, job_title)
        risk_analysis = self._risk_analysis(scores, candidate_data, job_data)
        confidence    = self._confidence_score(scores, candidate_data)

        return {
            "overall_match_percent": overall,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missing_skills": missing_skills,
            "why_ranked_here": why_ranked,
            "interview_recommendation": interview_rec,
            "hiring_recommendation": hiring_rec,
            "risk_analysis": risk_analysis,
            "confidence_score": confidence,
            "score_breakdown": {
                "overall": overall,
                "skills": scores.get("skills", 0),
                "projects": scores.get("projects", 0),
                "experience": scores.get("experience", 0),
                "education": scores.get("education", 0),
                "soft_skills": scores.get("soft_skills", 0),
                "industry": scores.get("industry", 0),
                "growth": scores.get("growth", 0),
                "github": scores.get("github", 0),
                "portfolio": scores.get("portfolio", 0),
                "certifications": scores.get("certifications", 0),
            },
            "semantic_similarity": scores.get("semantic_similarity", 0),
        }

    # ------------------------------------------------------------------
    # Strengths
    # ------------------------------------------------------------------

    def _identify_strengths(self, job: Dict, candidate: Dict, scores: Dict) -> List[str]:
        """Identify candidate strengths relative to the job."""
        strengths = []
        name = candidate.get("name", "The candidate")

        # High skill match
        if scores.get("skills", 0) >= 75:
            matching = self._get_matching_skills(job, candidate)[:5]
            if matching:
                strengths.append(f"Strong technical alignment — proficient in {', '.join(matching)}.")

        # Experience match
        if scores.get("experience", 0) >= 80:
            years = candidate.get("total_experience_years", 0)
            if years:
                strengths.append(f"Experience level matches well ({years:.0f} years of experience).")

        # Strong projects
        if scores.get("projects", 0) >= 70:
            proj_count = len(candidate.get("projects", []))
            if proj_count > 0:
                strengths.append(f"Has {proj_count} relevant project(s) demonstrating hands-on experience.")

        # GitHub presence
        if candidate.get("github_url"):
            strengths.append("Active GitHub profile indicates open-source involvement.")

        # Portfolio
        if candidate.get("portfolio_url"):
            strengths.append("Personal portfolio demonstrates initiative and professional presentation.")

        # Certifications
        certs = candidate.get("certifications", [])
        if certs:
            strengths.append(f"Holds {len(certs)} certification(s): {', '.join(certs[:2])}.")

        # Hackathons
        hackathons = candidate.get("hackathons", [])
        if hackathons:
            strengths.append(f"Hackathon participation shows competitive problem-solving ability.")

        # Deployment experience
        if candidate.get("deployment_experience"):
            strengths.append("Has hands-on deployment experience (Docker/Kubernetes/Cloud).")

        # Education match
        if scores.get("education", 0) >= 80:
            edu = candidate.get("education", [{}])
            degree = edu[0].get("degree", "") if edu else ""
            if degree:
                strengths.append(f"Educational background ({degree}) aligns with role requirements.")

        # Industry experience
        if scores.get("industry", 0) >= 70:
            domains = candidate.get("industry_domains", [])
            if domains:
                strengths.append(f"Relevant domain experience in {', '.join(domains[:2])}.")

        # High growth score
        if scores.get("growth", 0) >= 75:
            strengths.append("Career trajectory shows consistent growth and learning ability.")

        if not strengths:
            strengths.append("Candidate shows general alignment with the role requirements.")

        return strengths[:6]

    # ------------------------------------------------------------------
    # Weaknesses
    # ------------------------------------------------------------------

    def _identify_weaknesses(self, job: Dict, candidate: Dict, scores: Dict) -> List[str]:
        """Identify candidate gaps relative to the job."""
        weaknesses = []
        name = candidate.get("name", "The candidate")
        overall = scores.get("overall", 0)

        # Low skill match
        if scores.get("skills", 0) < 50:
            missing = self._find_missing_skills(job, candidate)[:3]
            if missing:
                weaknesses.append(f"Skill gaps identified — missing: {', '.join(missing)}.")

        # Experience gap
        if scores.get("experience", 0) < 50:
            req_exp = job.get("experience_years", "")
            candidate_years = candidate.get("total_experience_years", 0) or 0
            if req_exp and req_exp != "Not specified":
                weaknesses.append(f"Experience may be below the required {req_exp}.")

        # Weak projects
        if scores.get("projects", 0) < 40:
            proj_count = len(candidate.get("projects", []))
            if proj_count == 0:
                weaknesses.append("No relevant projects found in the profile.")
            else:
                weaknesses.append("Projects show limited relevance to the specific tech stack required.")

        # No GitHub
        if not candidate.get("github_url") and not candidate.get("open_source"):
            weaknesses.append("No public GitHub profile — makes it harder to assess coding style.")

        # No certifications
        if not candidate.get("certifications"):
            weaknesses.append("No certifications listed — additional credentials could strengthen the profile.")

        # Industry mismatch
        if scores.get("industry", 0) < 40:
            job_industry = job.get("industry", "")
            if job_industry:
                weaknesses.append(f"Limited prior experience in {job_industry} industry context.")

        # Education mismatch
        if scores.get("education", 0) < 50:
            weaknesses.append("Educational background may not fully meet the stated requirements.")

        # Growth concern
        if scores.get("growth", 0) < 40:
            weaknesses.append("Career progression data is limited — harder to assess growth trajectory.")

        if not weaknesses:
            if overall < 60:
                weaknesses.append("Overall profile alignment with this specific role is moderate.")
            else:
                weaknesses.append("Minor gaps exist but are addressable with onboarding support.")

        return weaknesses[:5]

    # ------------------------------------------------------------------
    # Missing Skills
    # ------------------------------------------------------------------

    def _find_missing_skills(self, job: Dict, candidate: Dict) -> List[str]:
        """Find required skills that the candidate is missing."""
        required = [s.lower() for s in job.get("required_skills", []) + job.get("tech_stack", [])]
        candidate_skills = [s.lower() for s in
                           candidate.get("skills", []) + candidate.get("technical_skills", [])]

        missing = []
        for skill in required:
            if not any(skill in cs or cs in skill for cs in candidate_skills):
                missing.append(skill.title() if len(skill.split()) == 1 else skill)

        return list(set(missing))[:8]

    def _get_matching_skills(self, job: Dict, candidate: Dict) -> List[str]:
        """Find skills that match between job and candidate."""
        required = [s.lower() for s in job.get("required_skills", []) + job.get("tech_stack", [])]
        candidate_skills = [s.lower() for s in
                           candidate.get("skills", []) + candidate.get("technical_skills", [])]

        matching = []
        for skill in required:
            if any(skill in cs or cs in skill for cs in candidate_skills):
                matching.append(skill.title() if len(skill.split()) == 1 else skill)

        return list(set(matching))[:8]

    # ------------------------------------------------------------------
    # Explanations
    # ------------------------------------------------------------------

    def _explain_ranking(self, overall: float, scores: Dict, job_title: str, name: str) -> str:
        """Generate an explanation of why this candidate is ranked at their position."""
        level = self._get_tier(overall)
        top_dim = max(["skills", "experience", "projects", "industry"],
                     key=lambda d: scores.get(d, 0))

        dim_labels = {
            "skills": "technical skill alignment",
            "experience": "relevant experience",
            "projects": "project portfolio",
            "industry": "industry domain knowledge",
        }

        if overall >= self.EXCELLENT:
            return (f"{name} scores in the top tier ({overall:.1f}%) for this role. "
                    f"Exceptional {dim_labels.get(top_dim, 'overall match')} makes them a "
                    f"highly competitive candidate for {job_title}.")
        elif overall >= self.GOOD:
            return (f"{name} is a strong candidate ({overall:.1f}% match). "
                    f"Particularly strong in {dim_labels.get(top_dim, 'key areas')}, "
                    f"with minor gaps that can be addressed during onboarding.")
        elif overall >= self.AVERAGE:
            return (f"{name} shows moderate alignment ({overall:.1f}%) with {job_title}. "
                    f"Best performance in {dim_labels.get(top_dim, 'some areas')}, "
                    f"but may need upskilling in certain required areas.")
        else:
            return (f"{name} currently shows limited alignment ({overall:.1f}%) with the role. "
                    f"Significant skill gaps identified. May be suitable for a more junior position "
                    f"or with substantial training investment.")

    def _interview_recommendation(self, overall: float, scores: Dict, name: str) -> str:
        """Generate interview recommendation."""
        if overall >= self.EXCELLENT:
            return (f"✅ Strongly recommend for immediate technical interview. "
                    f"{name} demonstrates exceptional alignment. "
                    f"Focus interview on system design and leadership competencies.")
        elif overall >= self.GOOD:
            return (f"✅ Recommend for technical interview. "
                    f"Assess the specific skill gaps identified during the technical round. "
                    f"Consider a take-home assignment to validate project skills.")
        elif overall >= self.AVERAGE:
            return (f"⚠️ Consider for screening interview first. "
                    f"Verify the candidate's claimed experience in key areas before proceeding. "
                    f"Assess learning agility and willingness to upskill.")
        else:
            return (f"❌ Not recommended for interview at this stage. "
                    f"Significant gaps in required competencies. "
                    f"Consider re-evaluating after candidate gains more experience.")

    def _hiring_recommendation(self, overall: float, scores: Dict, name: str, job: str) -> str:
        """Generate hiring recommendation."""
        if overall >= self.EXCELLENT:
            return f"🟢 STRONG HIRE – {name} is an exceptional match for {job}. Prioritize offer."
        elif overall >= self.GOOD:
            return f"🟡 HIRE – {name} is a good fit. Minor gaps are acceptable. Move forward."
        elif overall >= self.AVERAGE:
            return f"🟡 CONDITIONAL HIRE – Consider {name} if stronger candidates aren't available."
        elif overall >= self.POOR:
            return f"🔴 NO HIRE – {name} does not meet minimum requirements for {job} currently."
        else:
            return f"🔴 STRONG NO HIRE – Significant misalignment between {name}'s profile and {job}."

    def _risk_analysis(self, scores: Dict, candidate: Dict, job: Dict) -> str:
        """Analyze risk factors for hiring this candidate."""
        risks = []
        overall = scores.get("overall", 0)

        if scores.get("experience", 0) < 50:
            risks.append("experience gap")
        if scores.get("skills", 0) < 50:
            risks.append("skill mismatch")
        if not candidate.get("github_url") and not candidate.get("portfolio_url"):
            risks.append("limited verifiable work samples")
        if not candidate.get("email"):
            risks.append("contact information incomplete")
        if candidate.get("total_experience_years", 0) == 0:
            risks.append("no verifiable work history")

        if not risks:
            return ("Low risk profile. Candidate appears well-qualified with verifiable experience. "
                    "Standard reference checks recommended.")
        elif len(risks) == 1:
            return (f"Moderate risk: {risks[0]}. "
                    "Address during interview process. Overall profile remains acceptable.")
        else:
            return (f"Higher risk profile due to: {', '.join(risks)}. "
                    "Thorough technical assessment and reference verification recommended "
                    "before extending an offer.")

    def _confidence_score(self, scores: Dict, candidate: Dict) -> float:
        """
        Compute AI confidence in the analysis.
        Higher when more data points are available.
        """
        confidence = 50.0

        # More complete profile = higher confidence
        if candidate.get("experience"):
            confidence += 10
        if candidate.get("projects"):
            confidence += 10
        if candidate.get("education"):
            confidence += 5
        if candidate.get("skills"):
            confidence += 10
        if candidate.get("github_url") or candidate.get("portfolio_url"):
            confidence += 10
        if candidate.get("certifications"):
            confidence += 5

        return min(95.0, confidence)

    def _get_tier(self, score: float) -> str:
        if score >= self.EXCELLENT:
            return "excellent"
        elif score >= self.GOOD:
            return "good"
        elif score >= self.AVERAGE:
            return "average"
        else:
            return "poor"


scoring_engine = ScoringEngine()
