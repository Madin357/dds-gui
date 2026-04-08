from pydantic import BaseModel
from typing import Optional
import uuid


class KPIResponse(BaseModel):
    total_students: int = 0
    active_students: int = 0
    total_programs: int = 0
    avg_gpa: Optional[float] = None
    overall_attendance: Optional[float] = None
    overall_pass_rate: Optional[float] = None
    overall_dropout_rate: Optional[float] = None
    at_risk_students: int = 0
    high_risk_students: int = 0
    avg_program_score: Optional[float] = None
    avg_relevance_score: Optional[float] = None


class DashboardResponse(BaseModel):
    kpis: KPIResponse
    enrollment_trend: list[dict]
    risk_distribution: dict
    top_programs: list[dict]
    recent_recommendations: list[dict]


class EnrollmentTrendItem(BaseModel):
    period: str
    count: int
    program: Optional[str] = None


class RiskDistribution(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
