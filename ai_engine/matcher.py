"""
AI-based resume matching engine.

Uses keyword overlap and weighted scoring to calculate how well
a candidate's skills match the requirements of a job posting.
"""

from __future__ import annotations
import re
from collections import Counter


def _normalize(term: str) -> str:
    """Lower-case and strip punctuation for fair comparison."""
    return re.sub(r"[^a-z0-9+#.]", "", term.lower())


def _build_set(items) -> set[str]:
    """Accept a list of strings or a comma-separated string and return a normalized set."""
    if isinstance(items, str):
        items = [s.strip() for s in items.split(",") if s.strip()]
    if not items:
        return set()
    return {_normalize(t) for t in items}


def calculate_match_score(
    candidate_skills: list | str,
    job_requirements: list | str,
) -> float:
    """
    Return a 0 – 100 match score.

    Algorithm
    ---------
    1. Build normalized skill sets for candidate and job.
    2. Compute intersection / union (Jaccard similarity).
    3. Weight the result so partial matches still score reasonably.
    """
    cand = _build_set(candidate_skills)
    reqs = _build_set(job_requirements)

    if not reqs:
        return 100.0  # No requirements → perfect match by default
    if not cand:
        return 0.0

    matched = cand & reqs
    # Weighted: how many required skills the candidate covers
    coverage = len(matched) / len(reqs)
    # Bonus for extra skills (smaller weight)
    extra_ratio = max(0, len(cand) - len(reqs)) / max(len(cand), 1) * 0.1

    score = round(min((coverage + extra_ratio) * 100, 100.0), 1)
    return score


def explain_match(
    candidate_skills: list | str,
    job_requirements: list | str,
) -> dict:
    """Return a detailed breakdown of the match."""
    cand = _build_set(candidate_skills)
    reqs = _build_set(job_requirements)
    matched = cand & reqs
    missing = reqs - cand
    extra = cand - reqs

    return {
        "score": calculate_match_score(candidate_skills, job_requirements),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
        "coverage_pct": round(len(matched) / max(len(reqs), 1) * 100, 1),
    }
