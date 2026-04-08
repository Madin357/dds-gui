from typing import Optional
import uuid

from fastapi import APIRouter, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser
from app.models.student import Student
from app.models.enrollment import Enrollment
from app.models.program import Program
from app.models.attendance import AttendanceRecord
from app.models.assessment import Assessment
from app.models.course import Course
from app.models.analytics import AnalyticsStudentScore
from app.schemas.student import (
    StudentResponse, StudentDetailResponse, StudentListResponse,
    AttendanceResponse, AssessmentResponse,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=StudentListResponse)
async def list_students(
    user: CurrentUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    program_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
):
    inst_id = user.institution_id

    # Base query
    query = (
        select(
            Student,
            AnalyticsStudentScore.dropout_risk,
            AnalyticsStudentScore.performance_risk,
            AnalyticsStudentScore.attendance_rate,
        )
        .outerjoin(AnalyticsStudentScore, AnalyticsStudentScore.student_id == Student.id)
        .where(Student.institution_id == inst_id)
    )

    # Filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Student.first_name.ilike(search_term)) |
            (Student.last_name.ilike(search_term)) |
            (Student.student_code.ilike(search_term))
        )

    if program_id:
        query = query.join(Enrollment, Enrollment.student_id == Student.id).where(
            Enrollment.program_id == program_id
        )

    if status == "active":
        query = query.where(Student.is_active == True)
    elif status == "dropped":
        query = query.where(Student.is_active == False)

    if risk_level == "high":
        query = query.where(AnalyticsStudentScore.dropout_risk >= 70)
    elif risk_level == "medium":
        query = query.where(and_(AnalyticsStudentScore.dropout_risk >= 40, AnalyticsStudentScore.dropout_risk < 70))
    elif risk_level == "low":
        query = query.where(AnalyticsStudentScore.dropout_risk < 40)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Student.last_name).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for student, dropout_risk, perf_risk, att_rate in rows:
        items.append(StudentResponse(
            id=student.id,
            student_code=student.student_code,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            gender=student.gender,
            enrollment_date=student.enrollment_date,
            current_gpa=float(student.current_gpa) if student.current_gpa else None,
            current_semester=student.current_semester,
            is_active=student.is_active,
            dropout_risk=float(dropout_risk) if dropout_risk else None,
            performance_risk=float(perf_risk) if perf_risk else None,
            attendance_rate=float(att_rate) if att_rate else None,
        ))

    return StudentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/at-risk")
async def at_risk_students(user: CurrentUser, db: DB, limit: int = Query(20, le=100)):
    query = (
        select(Student, AnalyticsStudentScore)
        .join(AnalyticsStudentScore, AnalyticsStudentScore.student_id == Student.id)
        .where(
            Student.institution_id == user.institution_id,
            Student.is_active == True,
            AnalyticsStudentScore.dropout_risk >= 40,
        )
        .order_by(AnalyticsStudentScore.dropout_risk.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": str(s.id),
            "student_code": s.student_code,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "current_gpa": float(s.current_gpa) if s.current_gpa else None,
            "current_semester": s.current_semester,
            "dropout_risk": float(a.dropout_risk) if a.dropout_risk else None,
            "performance_risk": float(a.performance_risk) if a.performance_risk else None,
            "attendance_rate": float(a.attendance_rate) if a.attendance_rate else None,
            "gpa_trend": a.gpa_trend,
            "risk_factors": a.risk_factors,
        }
        for s, a in rows
    ]


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student(student_id: uuid.UUID, user: CurrentUser, db: DB):
    # Get student with analytics
    query = (
        select(Student, AnalyticsStudentScore)
        .outerjoin(AnalyticsStudentScore, AnalyticsStudentScore.student_id == Student.id)
        .where(Student.id == student_id, Student.institution_id == user.institution_id)
    )
    result = await db.execute(query)
    row = result.first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    student, analytics = row

    # Get program name
    enroll_q = (
        select(Program.name)
        .join(Enrollment, Enrollment.program_id == Program.id)
        .where(Enrollment.student_id == student_id)
        .limit(1)
    )
    program_result = await db.execute(enroll_q)
    program_name = program_result.scalar_one_or_none()

    return StudentDetailResponse(
        id=student.id,
        student_code=student.student_code,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        gender=student.gender,
        date_of_birth=student.date_of_birth,
        enrollment_date=student.enrollment_date,
        current_gpa=float(student.current_gpa) if student.current_gpa else None,
        current_semester=student.current_semester,
        is_active=student.is_active,
        dropout_risk=float(analytics.dropout_risk) if analytics and analytics.dropout_risk else None,
        performance_risk=float(analytics.performance_risk) if analytics and analytics.performance_risk else None,
        attendance_rate=float(analytics.attendance_rate) if analytics and analytics.attendance_rate else None,
        avg_score=float(analytics.avg_score) if analytics and analytics.avg_score else None,
        gpa_trend=analytics.gpa_trend if analytics else None,
        risk_factors=analytics.risk_factors if analytics else None,
        program_name=program_name,
    )


@router.get("/{student_id}/attendance", response_model=list[AttendanceResponse])
async def get_student_attendance(student_id: uuid.UUID, user: CurrentUser, db: DB):
    query = (
        select(AttendanceRecord, Course.name.label("course_name"))
        .join(Course, Course.id == AttendanceRecord.course_id)
        .where(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.institution_id == user.institution_id,
        )
        .order_by(AttendanceRecord.session_date.desc())
        .limit(200)
    )
    result = await db.execute(query)
    return [
        AttendanceResponse(
            id=att.id, course_name=cname, session_date=att.session_date, status=att.status
        )
        for att, cname in result.all()
    ]


@router.get("/{student_id}/assessments", response_model=list[AssessmentResponse])
async def get_student_assessments(student_id: uuid.UUID, user: CurrentUser, db: DB):
    query = (
        select(Assessment, Course.name.label("course_name"))
        .join(Course, Course.id == Assessment.course_id)
        .where(
            Assessment.student_id == student_id,
            Assessment.institution_id == user.institution_id,
        )
        .order_by(Assessment.assessed_at.desc())
    )
    result = await db.execute(query)
    return [
        AssessmentResponse(
            id=a.id, course_name=cname, type=a.type, title=a.title,
            score=float(a.score) if a.score else None,
            max_score=float(a.max_score),
            percentage=float(a.percentage) if a.percentage else (float(a.score / a.max_score * 100) if a.score and a.max_score else None),
            grade=a.grade, assessed_at=a.assessed_at,
        )
        for a, cname in result.all()
    ]
