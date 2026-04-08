from pydantic import BaseModel
from typing import Optional
import uuid


class ProgramResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: Optional[str] = None
    level: Optional[str] = None
    department: Optional[str] = None
    duration_months: Optional[int] = None
    is_active: bool
    # Analytics (joined)
    performance_score: Optional[float] = None
    completion_rate: Optional[float] = None
    pass_rate: Optional[float] = None
    avg_gpa: Optional[float] = None
    dropout_rate: Optional[float] = None
    enrollment_trend: Optional[str] = None
    relevance_score: Optional[float] = None
    demand_trend: Optional[str] = None
    student_count: Optional[int] = None

    class Config:
        from_attributes = True


class ProgramListResponse(BaseModel):
    items: list[ProgramResponse]
    total: int


class CourseResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: Optional[str] = None
    credits: Optional[float] = None
    semester: Optional[int] = None
    program_name: Optional[str] = None

    class Config:
        from_attributes = True
