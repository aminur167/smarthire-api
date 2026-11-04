"""
Candidate ranking engine.

Ranks candidates for a given job posting by combining AI match score,
experience level, and education quality into a composite score.
"""

from __future__ import annotations

_DEGREE_WEIGHTS = {
    "phd": 1.0,
    "ph.d": 1.0,
    "master": 0.85,
    "msc": 0.85,
    "mba": 0.85,
    "m.s": 0.85,
    "m.tech": 0.85,
    "bachelor": 0.7,
    "bsc": 0.7,
    "b.s": 0.7,
    "b.tech": 0.7,
    "b.a": 0.65,
    "associate": 0.5,
    "diploma": 0.4,
    "high school": 0.25,
}

_EXP_MAP = {
    "ENTRY": (0, 2),
    "MID": (3, 6),
    "SENIOR": (7, 12),
    "LEAD": (10, 25),
}


def _education_score(education_text: str) -> float:
    """Score education on a 0 – 1 scale based on highest degree found."""
    lower = education_text.lower()
    best = 0.0
    for keyword, weight in _DEGREE_WEIGHTS.items():
        if keyword in lower:
            best = max(best, weight)
    return best


def _experience_score(years: int, experience_level: str) -> float:
    """Score 0 – 1 based on how well candidate experience matches the job level."""
    lo, hi = _EXP_MAP.get(experience_level, (0, 99))
    if lo <= years <= hi:
        return 1.0
    if years < lo:
        return max(0, 1 - (lo - years) * 0.15)
    return max(0.5, 1 - (years - hi) * 0.05)  # Overqualified is still okay


def rank_candidates(candidates_data: list[dict], job: dict) -> list[dict]:
    """
    Rank a list of candidate dicts for a job dict.

    Parameters
    ----------
    candidates_data : list[dict]
        Each dict must have: id, name, ai_match_score, experience_years, education
    job : dict
        Must have: experience_level

    Returns
    -------
    list[dict] sorted by composite_score descending
    """
    experience_level = job.get("experience_level", "MID")
    results = []

    for c in candidates_data:
        ai_score = c.get("ai_match_score", 0) / 100.0
        exp_score = _experience_score(c.get("experience_years", 0), experience_level)
        edu_score = _education_score(c.get("education", ""))

        # Weighted composite: skills 50%, experience 30%, education 20%
        composite = round((ai_score * 0.50 + exp_score * 0.30 + edu_score * 0.20) * 100, 1)

        results.append({
            **c,
            "composite_score": composite,
            "breakdown": {
                "skill_match": round(ai_score * 100, 1),
                "experience_fit": round(exp_score * 100, 1),
                "education_quality": round(edu_score * 100, 1),
            },
        })

    results.sort(key=lambda x: x["composite_score"], reverse=True)

    for rank, item in enumerate(results, start=1):
        item["rank"] = rank

    return results
