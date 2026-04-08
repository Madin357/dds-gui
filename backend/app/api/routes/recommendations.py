import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.deps import DB, CurrentUser
from app.models.recommendation import Recommendation
from app.models.labour_market import LabourMarketTrend, SkillTrend
from app.schemas.recommendation import (
    RecommendationResponse, RecommendationListResponse, UpdateRecommendationStatus,
    LabourMarketTrendResponse, SkillTrendResponse,
)

router = APIRouter(tags=["recommendations"])


# --- Recommendations ---

@router.get("/recommendations", response_model=RecommendationListResponse)
async def list_recommendations(
    user: CurrentUser, db: DB,
    level: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = Query("active"),
):
    query = select(Recommendation).where(Recommendation.institution_id == user.institution_id)
    if level:
        query = query.where(Recommendation.level == level)
    if category:
        query = query.where(Recommendation.category == category)
    if status:
        query = query.where(Recommendation.status == status)
    query = query.order_by(Recommendation.priority_score.desc().nullslast())

    result = await db.execute(query)
    items = [RecommendationResponse.model_validate(r) for r in result.scalars().all()]
    return RecommendationListResponse(items=items, total=len(items))


@router.get("/recommendations/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(rec_id: uuid.UUID, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == rec_id, Recommendation.institution_id == user.institution_id)
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return RecommendationResponse.model_validate(rec)


@router.put("/recommendations/{rec_id}/status")
async def update_recommendation_status(rec_id: uuid.UUID, req: UpdateRecommendationStatus, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == rec_id, Recommendation.institution_id == user.institution_id)
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = req.status
    await db.commit()
    return {"message": "Status updated", "new_status": req.status}


# --- Labour Market ---

@router.get("/labour-market/trends", response_model=list[LabourMarketTrendResponse])
async def list_labour_market_trends(user: CurrentUser, db: DB):
    query = select(LabourMarketTrend).order_by(LabourMarketTrend.growth_rate.desc().nullslast()).limit(50)
    result = await db.execute(query)
    return [LabourMarketTrendResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/labour-market/skills", response_model=list[SkillTrendResponse])
async def list_skill_trends(user: CurrentUser, db: DB):
    query = select(SkillTrend).order_by(SkillTrend.growth_rate.desc().nullslast()).limit(50)
    result = await db.execute(query)
    return [SkillTrendResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/labour-market/alignment")
async def programme_alignment(user: CurrentUser, db: DB):
    """Program-to-market alignment scores."""
    from app.models.program import Program
    from app.models.analytics import AnalyticsProgramScore

    query = (
        select(Program.name, Program.code, AnalyticsProgramScore.relevance_score, AnalyticsProgramScore.demand_trend)
        .join(AnalyticsProgramScore, AnalyticsProgramScore.program_id == Program.id)
        .where(Program.institution_id == user.institution_id)
        .order_by(AnalyticsProgramScore.relevance_score.desc().nullslast())
    )
    result = await db.execute(query)
    return [
        {"name": r.name, "code": r.code,
         "relevance_score": float(r.relevance_score) if r.relevance_score else None,
         "demand_trend": r.demand_trend}
        for r in result.all()
    ]
