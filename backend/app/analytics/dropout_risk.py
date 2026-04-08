"""
Dropout risk scoring (0-100). Higher = more likely to drop out.

Factors:
  - attendance_rate (w=0.30)
  - performance / GPA (w=0.25)
  - assessment completion (w=0.20)
  - semester (first-year = higher base risk) (w=0.10)
  - GPA trend (w=0.15)
"""


def attendance_factor(rate: float | None) -> float:
    if rate is None:
        return 50
    if rate >= 90:
        return 0
    if rate >= 80:
        return 20
    if rate >= 70:
        return 45
    if rate >= 60:
        return 70
    return 95


def performance_factor(gpa: float | None) -> float:
    if gpa is None:
        return 50
    if gpa >= 3.5:
        return 0
    if gpa >= 3.0:
        return 15
    if gpa >= 2.5:
        return 35
    if gpa >= 2.0:
        return 60
    return 90


def assessment_completion_factor(completion_pct: float | None) -> float:
    if completion_pct is None:
        return 30
    if completion_pct >= 95:
        return 0
    if completion_pct >= 85:
        return 20
    if completion_pct >= 70:
        return 50
    return 85


def semester_factor(semester: int | None) -> float:
    if semester is None:
        return 30
    if semester <= 1:
        return 60
    if semester <= 2:
        return 40
    if semester <= 4:
        return 20
    return 10


def trend_factor(trend: str | None) -> float:
    if trend is None:
        return 25
    if trend == "improving":
        return 0
    if trend == "stable":
        return 25
    if trend == "declining":
        return 60
    return 90  # sharp_decline


def compute_dropout_risk(
    attendance_rate: float | None,
    gpa: float | None,
    assessment_completion: float | None,
    current_semester: int | None,
    gpa_trend: str | None,
) -> float:
    score = (
        0.30 * attendance_factor(attendance_rate) +
        0.25 * performance_factor(gpa) +
        0.20 * assessment_completion_factor(assessment_completion) +
        0.10 * semester_factor(current_semester) +
        0.15 * trend_factor(gpa_trend)
    )
    return round(min(100, max(0, score)), 2)
