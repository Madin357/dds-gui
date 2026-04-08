"""
Program performance score (0-100). Higher = better performing program.
Also computes relevance score for labour market alignment.
"""


def compute_program_score(
    completion_rate: float | None,
    avg_gpa: float | None,
    pass_rate: float | None,
    relevance_score: float | None,
    enrollment_trend: str | None,
) -> float:
    cr = (completion_rate or 0) / 100 * 100
    gpa_norm = ((avg_gpa or 0) / 4.0) * 100
    pr = (pass_rate or 0) / 100 * 100
    rel = relevance_score or 50

    trend_val = {"growing": 80, "stable": 60, "declining": 30}.get(enrollment_trend or "stable", 60)

    score = 0.25 * cr + 0.20 * gpa_norm + 0.20 * pr + 0.20 * rel + 0.15 * trend_val
    return round(min(100, max(0, score)), 2)


def compute_relevance_score(
    skills_overlap_pct: float | None,
    sector_growth: float | None,
    demand_level: str | None,
) -> float:
    """How well a program aligns with labour market demand."""
    # Skills overlap
    if skills_overlap_pct is None:
        so = 50
    elif skills_overlap_pct > 70:
        so = 90
    elif skills_overlap_pct > 50:
        so = 65
    elif skills_overlap_pct > 30:
        so = 40
    else:
        so = 15

    # Sector growth
    if sector_growth is None:
        sg = 50
    elif sector_growth > 20:
        sg = 90
    elif sector_growth > 10:
        sg = 65
    elif sector_growth > 0:
        sg = 40
    else:
        sg = 15

    # Demand
    dl = {"high": 90, "medium": 55, "low": 25, "declining": 10}.get(demand_level or "medium", 55)

    score = 0.40 * so + 0.30 * sg + 0.30 * dl
    return round(min(100, max(0, score)), 2)
