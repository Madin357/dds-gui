from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid


class StudentResponse(BaseModel):
    id: uuid.UUID
    student_code: Optional[str] = None
    first_name: str
    last_name: str
    email: Optional[str] = None
    gender: Optional[str] = None
    enrollment_date: Optional[date] = None
    current_gpa: Optional[float] = None
    current_semester: Optional[int] = None
    is_active: bool
    # Analytics fields (joined from analytics_student_scores)
    dropout_risk: Optional[float] = None
    performance_risk: Optional[float] = None
    attendance_rate: Optional[float] = None

    class Config:
        from_attributes = True


class StudentDetailResponse(StudentResponse):
    date_of_birth: Optional[date] = None
    avg_score: Optional[float] = None
    gpa_trend: Optional[str] = None
    risk_factors: Optional[dict] = None
    program_name: Optional[str] = None


class StudentListResponse(BaseModel):
    items: list[StudentResponse]
    total: int
    page: int
    page_size: int


class AttendanceResponse(BaseModel):
    id: uuid.UUID
    course_name: Optional[str] = None
    session_date: date
    status: str

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    course_name: Optional[str] = None
    type: str
    title: Optional[str] = None
    score: Optional[float] = None
    max_score: float
    percentage: Optional[float] = None
    grade: Optional[str] = None
    assessed_at: date

    class Config:
        from_attributes = True
