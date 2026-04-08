from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.deps import DB, CurrentUser
from app.models.program import Program
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.analytics import AnalyticsProgramScore
from app.schemas.program import ProgramResponse, ProgramListResponse, CourseResponse

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("", response_model=ProgramListResponse)
async def list_programs(user: CurrentUser, db: DB):
    query = (
        select(
            Program,
            AnalyticsProgramScore,
            func.count(Enrollment.id).label("student_count"),
        )
        .outerjoin(AnalyticsProgramScore, AnalyticsProgramScore.program_id == Program.id)
        .outerjoin(Enrollment, (Enrollment.program_id == Program.id) & (Enrollment.status == "active"))
        .where(Program.institution_id == user.institution_id)
        .group_by(Program.id, AnalyticsProgramScore.id)
        .order_by(Program.name)
    )
    result = await db.execute(query)
    rows = result.all()

    items = []
    for prog, analytics, student_count in rows:
        items.append(ProgramResponse(
            id=prog.id,
            name=prog.name,
            code=prog.code,
            level=prog.level,
            department=prog.department,
            duration_months=prog.duration_months,
            is_active=prog.is_active,
            performance_score=float(analytics.performance_score) if analytics and analytics.performance_score else None,
            completion_rate=float(analytics.completion_rate) if analytics and analytics.completion_rate else None,
            pass_rate=float(analytics.pass_rate) if analytics and analytics.pass_rate else None,
            avg_gpa=float(analytics.avg_gpa) if analytics and analytics.avg_gpa else None,
            dropout_rate=float(analytics.dropout_rate) if analytics and analytics.dropout_rate else None,
            enrollment_trend=analytics.enrollment_trend if analytics else None,
            relevance_score=float(analytics.relevance_score) if analytics and analytics.relevance_score else None,
            demand_trend=analytics.demand_trend if analytics else None,
            student_count=student_count,
        ))

    return ProgramListResponse(items=items, total=len(items))


@router.get("/comparison")
async def compare_programs(user: CurrentUser, db: DB):
    """Side-by-side program comparison with all metrics."""
    query = (
        select(Program, AnalyticsProgramScore)
        .outerjoin(AnalyticsProgramScore, AnalyticsProgramScore.program_id == Program.id)
        .where(Program.institution_id == user.institution_id, Program.is_active == True)
        .order_by(AnalyticsProgramScore.performance_score.desc().nullslast())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "code": p.code,
            "performance_score": float(a.performance_score) if a and a.performance_score else None,
            "completion_rate": float(a.completion_rate) if a and a.completion_rate else None,
            "pass_rate": float(a.pass_rate) if a and a.pass_rate else None,
            "avg_gpa": float(a.avg_gpa) if a and a.avg_gpa else None,
            "dropout_rate": float(a.dropout_rate) if a and a.dropout_rate else None,
            "enrollment_trend": a.enrollment_trend if a else None,
            "relevance_score": float(a.relevance_score) if a and a.relevance_score else None,
        }
        for p, a in rows
    ]


@router.get("/{program_id}")
async def get_program(program_id: uuid.UUID, user: CurrentUser, db: DB):
    query = (
        select(Program, AnalyticsProgramScore)
        .outerjoin(AnalyticsProgramScore, AnalyticsProgramScore.program_id == Program.id)
        .where(Program.id == program_id, Program.institution_id == user.institution_id)
    )
    result = await db.execute(query)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Program not found")

    prog, analytics = row

    # Student count
    count_q = select(func.count()).where(Enrollment.program_id == program_id, Enrollment.status == "active")
    student_count = (await db.execute(count_q)).scalar() or 0

    return {
        "id": str(prog.id),
        "name": prog.name,
        "code": prog.code,
        "level": prog.level,
        "department": prog.department,
        "duration_months": prog.duration_months,
        "student_count": student_count,
        **(
            {
                "performance_score": float(analytics.performance_score) if analytics.performance_score else None,
                "completion_rate": float(analytics.completion_rate) if analytics.completion_rate else None,
                "pass_rate": float(analytics.pass_rate) if analytics.pass_rate else None,
                "avg_gpa": float(analytics.avg_gpa) if analytics.avg_gpa else None,
                "dropout_rate": float(analytics.dropout_rate) if analytics.dropout_rate else None,
                "enrollment_trend": analytics.enrollment_trend,
                "relevance_score": float(analytics.relevance_score) if analytics.relevance_score else None,
                "demand_trend": analytics.demand_trend,
            }
            if analytics
            else {}
        ),
    }


@router.get("/{program_id}/courses", response_model=list[CourseResponse])
async def get_program_courses(program_id: uuid.UUID, user: CurrentUser, db: DB):
    query = (
        select(Course)
        .where(Course.program_id == program_id, Course.institution_id == user.institution_id)
        .order_by(Course.semester, Course.name)
    )
    result = await db.execute(query)
    courses = result.scalars().all()
    return [
        CourseResponse(
            id=c.id, name=c.name, code=c.code,
            credits=float(c.credits) if c.credits else None,
            semester=c.semester,
        )
        for c in courses
    ]
