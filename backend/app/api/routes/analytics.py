from fastapi import APIRouter
from sqlalchemy import select, func, case, extract

from app.api.deps import DB, CurrentUser
from app.models.student import Student
from app.models.program import Program
from app.models.enrollment import Enrollment
from app.models.analytics import AnalyticsStudentScore, AnalyticsProgramScore, AnalyticsInstitutionKPI
from app.models.recommendation import Recommendation
from app.schemas.analytics import DashboardResponse, KPIResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(user: CurrentUser, db: DB):
    inst_id = user.institution_id

    # KPIs from cache
    kpi_q = select(AnalyticsInstitutionKPI).where(
        AnalyticsInstitutionKPI.institution_id == inst_id,
        AnalyticsInstitutionKPI.period == "latest",
    )
    kpi_result = await db.execute(kpi_q)
    kpi = kpi_result.scalar_one_or_none()

    if kpi:
        kpis = KPIResponse(
            total_students=kpi.total_students or 0,
            active_students=kpi.active_students or 0,
            total_programs=kpi.total_programs or 0,
            avg_gpa=float(kpi.avg_gpa) if kpi.avg_gpa else None,
            overall_attendance=float(kpi.overall_attendance) if kpi.overall_attendance else None,
            overall_pass_rate=float(kpi.overall_pass_rate) if kpi.overall_pass_rate else None,
            overall_dropout_rate=float(kpi.overall_dropout_rate) if kpi.overall_dropout_rate else None,
            at_risk_students=kpi.at_risk_students or 0,
            high_risk_students=kpi.high_risk_students or 0,
            avg_program_score=float(kpi.avg_program_score) if kpi.avg_program_score else None,
            avg_relevance_score=float(kpi.avg_relevance_score) if kpi.avg_relevance_score else None,
        )
    else:
        # Fallback: compute on the fly
        total = (await db.execute(select(func.count()).where(Student.institution_id == inst_id))).scalar() or 0
        active = (await db.execute(select(func.count()).where(Student.institution_id == inst_id, Student.is_active == True))).scalar() or 0
        programs = (await db.execute(select(func.count()).where(Program.institution_id == inst_id))).scalar() or 0
        avg_gpa = (await db.execute(select(func.avg(Student.current_gpa)).where(Student.institution_id == inst_id, Student.is_active == True))).scalar()

        at_risk = (await db.execute(
            select(func.count()).select_from(AnalyticsStudentScore).where(
                AnalyticsStudentScore.institution_id == inst_id,
                AnalyticsStudentScore.dropout_risk >= 40,
            )
        )).scalar() or 0
        high_risk = (await db.execute(
            select(func.count()).select_from(AnalyticsStudentScore).where(
                AnalyticsStudentScore.institution_id == inst_id,
                AnalyticsStudentScore.dropout_risk >= 70,
            )
        )).scalar() or 0

        kpis = KPIResponse(
            total_students=total,
            active_students=active,
            total_programs=programs,
            avg_gpa=round(float(avg_gpa), 2) if avg_gpa else None,
            at_risk_students=at_risk,
            high_risk_students=high_risk,
        )

    # Enrollment trend by year
    enroll_trend_q = (
        select(
            extract("year", Enrollment.enrolled_at).label("year"),
            func.count().label("count"),
        )
        .where(Enrollment.institution_id == inst_id)
        .group_by("year")
        .order_by("year")
    )
    enroll_result = await db.execute(enroll_trend_q)
    enrollment_trend = [{"period": str(int(r.year)), "count": r.count} for r in enroll_result.all()]

    # Risk distribution
    risk_q = (
        select(
            func.count().filter(AnalyticsStudentScore.dropout_risk >= 70).label("high"),
            func.count().filter(AnalyticsStudentScore.dropout_risk.between(40, 69.99)).label("medium"),
            func.count().filter(AnalyticsStudentScore.dropout_risk < 40).label("low"),
        )
        .where(AnalyticsStudentScore.institution_id == inst_id)
    )
    risk_result = await db.execute(risk_q)
    risk_row = risk_result.first()
    risk_distribution = {"high": risk_row.high or 0, "medium": risk_row.medium or 0, "low": risk_row.low or 0} if risk_row else {"high": 0, "medium": 0, "low": 0}

    # Top programs
    top_progs_q = (
        select(Program.name, AnalyticsProgramScore.performance_score, AnalyticsProgramScore.completion_rate)
        .join(AnalyticsProgramScore, AnalyticsProgramScore.program_id == Program.id)
        .where(Program.institution_id == inst_id)
        .order_by(AnalyticsProgramScore.performance_score.desc())
        .limit(5)
    )
    top_result = await db.execute(top_progs_q)
    top_programs = [
        {"name": r.name, "performance_score": float(r.performance_score) if r.performance_score else None,
         "completion_rate": float(r.completion_rate) if r.completion_rate else None}
        for r in top_result.all()
    ]

    # Recent recommendations
    rec_q = (
        select(Recommendation)
        .where(Recommendation.institution_id == inst_id, Recommendation.status == "active")
        .order_by(Recommendation.priority_score.desc())
        .limit(5)
    )
    rec_result = await db.execute(rec_q)
    recent_recs = [
        {"id": str(r.id), "title": r.title, "category": r.category, "level": r.level,
         "priority_score": float(r.priority_score) if r.priority_score else None}
        for r in rec_result.scalars().all()
    ]

    return DashboardResponse(
        kpis=kpis,
        enrollment_trend=enrollment_trend,
        risk_distribution=risk_distribution,
        top_programs=top_programs,
        recent_recommendations=recent_recs,
    )


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(user: CurrentUser, db: DB):
    kpi_q = select(AnalyticsInstitutionKPI).where(
        AnalyticsInstitutionKPI.institution_id == user.institution_id,
        AnalyticsInstitutionKPI.period == "latest",
    )
    result = await db.execute(kpi_q)
    kpi = result.scalar_one_or_none()
    if not kpi:
        return KPIResponse()
    return KPIResponse(
        total_students=kpi.total_students or 0,
        active_students=kpi.active_students or 0,
        total_programs=kpi.total_programs or 0,
        avg_gpa=float(kpi.avg_gpa) if kpi.avg_gpa else None,
        overall_attendance=float(kpi.overall_attendance) if kpi.overall_attendance else None,
        overall_pass_rate=float(kpi.overall_pass_rate) if kpi.overall_pass_rate else None,
        overall_dropout_rate=float(kpi.overall_dropout_rate) if kpi.overall_dropout_rate else None,
        at_risk_students=kpi.at_risk_students or 0,
        high_risk_students=kpi.high_risk_students or 0,
    )
