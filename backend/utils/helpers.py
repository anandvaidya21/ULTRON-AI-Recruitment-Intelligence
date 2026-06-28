"""ULTRON AI – General Utility Functions"""

import re
import json
import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


def generate_session_id() -> str:
    """Generate a unique chat session ID."""
    return str(uuid.uuid4())


def clean_text(text: str) -> str:
    """Normalize whitespace and remove special characters for processing."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    """Extract first email address from text."""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract first phone number from text."""
    patterns = [
        r'\+?\d[\d\s\-\(\)]{8,15}\d',
        r'\b\d{10}\b',
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = re.sub(r'[^\d+]', '', match.group(0))
            if len(phone) >= 10:
                return match.group(0).strip()
    return None


def extract_urls(text: str) -> Dict[str, Optional[str]]:
    """Extract GitHub, LinkedIn, and portfolio URLs from text."""
    urls: Dict[str, Optional[str]] = {
        "github": None,
        "linkedin": None,
        "portfolio": None,
    }
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    found = re.findall(url_pattern, text)

    for url in found:
        url_lower = url.lower()
        if "github.com" in url_lower and not urls["github"]:
            urls["github"] = url
        elif "linkedin.com" in url_lower and not urls["linkedin"]:
            urls["linkedin"] = url
        elif not urls["portfolio"] and "github" not in url_lower and "linkedin" not in url_lower:
            urls["portfolio"] = url

    return urls


def extract_years_of_experience(text: str) -> Optional[float]:
    """Heuristically extract years of experience from text."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+of\s+exp',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def detect_career_level(years: Optional[float], title: Optional[str]) -> str:
    """Detect career level from years of experience and title."""
    title_lower = (title or "").lower()
    if any(w in title_lower for w in ["senior", "lead", "principal", "staff", "architect"]):
        return "Senior"
    if any(w in title_lower for w in ["junior", "fresher", "entry", "intern"]):
        return "Junior"
    if any(w in title_lower for w in ["manager", "director", "vp", "head", "chief"]):
        return "Leadership"

    if years is not None:
        if years <= 1:
            return "Intern/Fresher"
        elif years <= 3:
            return "Junior"
        elif years <= 6:
            return "Mid-level"
        elif years <= 10:
            return "Senior"
        else:
            return "Lead/Principal"

    return "Mid-level"


def safe_json_load(text: str) -> Optional[Dict]:
    """Safely parse JSON, returning None on failure."""
    try:
        # Try to extract JSON block from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_match:
            return json.loads(json_match.group(1))
        return json.loads(text)
    except Exception:
        return None


def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a float value between min and max."""
    return max(min_val, min(max_val, value))


def format_score(score: float) -> str:
    """Format a score as a percentage string."""
    return f"{score:.1f}%"


def hash_file(file_bytes: bytes) -> str:
    """Return SHA256 hash of file bytes for dedup."""
    return hashlib.sha256(file_bytes).hexdigest()


def serialize_embedding(embedding) -> str:
    """Serialize a numpy array to JSON string for DB storage."""
    import json
    try:
        return json.dumps(embedding.tolist())
    except Exception:
        return "[]"


def deserialize_embedding(embedding_str: str):
    """Deserialize a JSON string back to numpy array."""
    import json
    import numpy as np
    try:
        return np.array(json.loads(embedding_str))
    except Exception:
        return None


def truncate_text(text: str, max_chars: int = 2000) -> str:
    """Truncate text to a maximum number of characters."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def current_timestamp() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.utcnow().isoformat()
