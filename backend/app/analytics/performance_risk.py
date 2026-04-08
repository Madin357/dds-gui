"""
Low-performance risk scoring (0-100). Higher = worse performance.

Factors:
  - GPA deviation from program average (w=0.35)
  - Recent assessment scores (w=0.30)
  - Attendance rate (w=0.20)
  - Failed assessments percentage (w=0.15)
"""


def gpa_deviation_factor(student_gpa: float | None, program_avg: float | None) -> float:
    if student_gpa is None or program_avg is None:
        return 40
    diff = program_avg - student_gpa
    if diff <= 0:
        return 0
    if diff <= 0.5:
        return 30
    if diff <= 1.0:
        return 60
    return 90


def recent_scores_factor(avg_recent: float | None) -> float:
    if avg_recent is None:
        return 40
    if avg_recent >= 80:
        return 0
    if avg_recent >= 70:
        return 25
    if avg_recent >= 60:
        return 50
    if avg_recent >= 50:
        return 75
    return 95


def attendance_penalty(rate: float | None) -> float:
    if rate is None:
        return 30
    if rate >= 85:
        return 0
    if rate >= 75:
        return 20
    if rate >= 65:
        return 50
    return 80


def failed_assessments_factor(fail_pct: float | None) -> float:
    if fail_pct is None:
        return 20
    if fail_pct == 0:
        return 0
    if fail_pct <= 10:
        return 20
    if fail_pct <= 25:
        return 50
    return 85


def compute_performance_risk(
    student_gpa: float | None,
    program_avg_gpa: float | None,
    avg_recent_score: float | None,
    attendance_rate: float | None,
    fail_percentage: float | None,
) -> float:
    score = (
        0.35 * gpa_deviation_factor(student_gpa, program_avg_gpa) +
        0.30 * recent_scores_factor(avg_recent_score) +
        0.20 * attendance_penalty(attendance_rate) +
        0.15 * failed_assessments_factor(fail_percentage)
    )
    return round(min(100, max(0, score)), 2)
