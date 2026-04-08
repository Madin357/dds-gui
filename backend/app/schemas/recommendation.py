from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    level: str
    target_id: Optional[uuid.UUID] = None
    category: str
    title: str
    description: str
    ai_generated: bool
    priority_score: Optional[float] = None
    status: str
    data_snapshot: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    items: list[RecommendationResponse]
    total: int


class UpdateRecommendationStatus(BaseModel):
    status: str  # 'accepted', 'dismissed', 'implemented'


class LabourMarketTrendResponse(BaseModel):
    id: uuid.UUID
    occupation: str
    sector: Optional[str] = None
    demand_level: Optional[str] = None
    growth_rate: Optional[float] = None
    avg_salary_azn: Optional[float] = None
    job_postings: Optional[int] = None

    class Config:
        from_attributes = True


class SkillTrendResponse(BaseModel):
    id: uuid.UUID
    skill_name: str
    category: Optional[str] = None
    demand_level: Optional[str] = None
    growth_rate: Optional[float] = None
    future_outlook: Optional[str] = None

    class Config:
        from_attributes = True
