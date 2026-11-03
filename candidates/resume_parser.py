"""Resume parsing utilities – extract text and structure from PDF resumes."""

import re
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def extract_text_from_pdf(file_path) -> str:
    """Read all pages of a PDF and return plain text."""
    if PdfReader is None:
        return ""
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


# ── Regex helpers ───────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}")
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE)

_SKILL_KEYWORDS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
    "Spring", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "SQL",
    "PostgreSQL", "MongoDB", "Redis", "Git", "Linux", "REST", "GraphQL",
    "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch",
    "HTML", "CSS", "Tailwind", "Next.js", "Figma", "Agile", "Scrum",
    "CI/CD", "Jenkins", "Terraform", "Ansible",
]

_DEGREE_RE = re.compile(
    r"(Bachelor|Master|PhD|B\.?S\.?c?|M\.?S\.?c?|B\.?A\.?|M\.?A\.?|B\.?Tech|M\.?Tech|MBA|Ph\.?D)",
    re.IGNORECASE,
)


def parse_resume(text: str) -> dict:
    """Return structured data extracted from resume text."""
    emails = _EMAIL_RE.findall(text)
    phones = _PHONE_RE.findall(text)
    linkedin_matches = _LINKEDIN_RE.findall(text)

    found_skills = []
    text_lower = text.lower()
    for skill in _SKILL_KEYWORDS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    degrees = _DEGREE_RE.findall(text)

    # Estimate experience years
    year_matches = re.findall(r"(\d{1,2})\s*\+?\s*years?\s*(of)?\s*experience", text, re.IGNORECASE)
    experience_years = int(year_matches[0][0]) if year_matches else 0

    return {
        "email": emails[0] if emails else "",
        "phone": phones[0].strip() if phones else "",
        "linkedin": f"https://{linkedin_matches[0]}" if linkedin_matches else "",
        "skills": found_skills,
        "degrees": list(set(degrees)),
        "experience_years": experience_years,
        "raw_text_length": len(text),
    }


def parse_resume_file(file_path) -> dict:
    """Full pipeline: PDF → text → structured data."""
    text = extract_text_from_pdf(file_path)
    if not text:
        return {"error": "Could not extract text from PDF", "skills": [], "experience_years": 0}
    return parse_resume(text)
