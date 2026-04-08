"""
Analytics aggregator — computes all scores and KPIs for an institution.
Runs as a Celery task or can be triggered manually.
"""

import json
import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.models.student import Student
from app.models.program import Program
from app.models.enrollment import Enrollment
from app.models.attendance import AttendanceRecord
from app.models.assessment import Assessment
from app.models.analytics import AnalyticsStudentScore, AnalyticsProgramScore, AnalyticsInstitutionKPI
from app.analytics.dropout_risk import compute_dropout_risk
from app.analytics.performance_risk import compute_performance_risk
from app.analytics.program_score import compute_program_score, compute_relevance_score

logger = logging.getLogger(__name__)

# Mapping of program codes/names to demand levels and growth rates
PROGRAM_MARKET_DATA = {
    "Computer Science": {"demand": "high", "growth": 22, "skills_overlap": 75},
    "CS": {"demand": "high", "growth": 22, "skills_overlap": 75},
    "Data Science": {"demand": "high", "growth": 30, "skills_overlap": 80},
    "DS": {"demand": "high", "growth": 30, "skills_overlap": 80},
    "Business Administration": {"demand": "medium", "growth": 8, "skills_overlap": 50},
    "BA": {"demand": "medium", "growth": 8, "skills_overlap": 50},
    "Civil Engineering": {"demand": "medium", "growth": 8, "skills_overlap": 55},
    "CE": {"demand": "medium", "growth": 8, "skills_overlap": 55},
    "Medicine": {"demand": "high", "growth": 12, "skills_overlap": 70},
    "MED": {"demand": "high", "growth": 12, "skills_overlap": 70},
    "Azerbaijani Language & Literature": {"demand": "low", "growth": -5, "skills_overlap": 20},
    "ALL": {"demand": "low", "growth": -5, "skills_overlap": 20},
    "Web Development": {"demand": "high", "growth": 18, "skills_overlap": 80},
    "WEB": {"demand": "high", "growth": 18, "skills_overlap": 80},
    "Digital Marketing": {"demand": "medium", "growth": 5, "skills_overlap": 55},
    "DM": {"demand": "medium", "growth": 5, "skills_overlap": 55},
    "UI/UX Design": {"demand": "high", "growth": 15, "skills_overlap": 65},
    "UX": {"demand": "high", "growth": 15, "skills_overlap": 65},
    "Cybersecurity": {"demand": "high", "growth": 25, "skills_overlap": 70},
    "CYB": {"demand": "high", "growth": 25, "skills_overlap": 70},
    "Cloud Computing": {"demand": "high", "growth": 28, "skills_overlap": 72},
    "CLD": {"demand": "high", "growth": 28, "skills_overlap": 72},
    "Project Management": {"demand": "medium", "growth": 6, "skills_overlap": 45},
    "PM": {"demand": "medium", "growth": 6, "skills_overlap": 45},
    "AI & Machine Learning": {"demand": "high", "growth": 35, "skills_overlap": 78},
    "AIML": {"demand": "high", "growth": 35, "skills_overlap": 78},
}


def compute_student_scores(db: Session, institution_id: str):
    """Compute dropout risk and performance risk for all students of an institution."""
    inst_uuid = institution_id
    students = db.query(Student).filter(Student.institution_id == inst_uuid, Student.is_active == True).all()
    logger.info(f"Computing scores for {len(students)} active students in {institution_id}")

    # Get program averages
    program_avgs = {}
    avg_rows = (
        db.query(Enrollment.program_id, func.avg(Student.current_gpa))
        .join(Student, Student.id == Enrollment.student_id)
        .filter(Enrollment.institution_id == inst_uuid, Student.is_active == True)
        .group_by(Enrollment.program_id)
        .all()
    )
    for pid, avg_gpa in avg_rows:
        program_avgs[pid] = float(avg_gpa) if avg_gpa else None

    for student in students:
        # Attendance rate
        total_att = db.query(func.count()).filter(
            AttendanceRecord.student_id == student.id,
        ).scalar() or 0
        present_att = db.query(func.count()).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.status.in_(["present", "late"]),
        ).scalar() or 0
        attendance_rate = (present_att / total_att * 100) if total_att > 0 else None

        # Average assessment score
        avg_score_row = db.query(func.avg(Assessment.score)).filter(
            Assessment.student_id == student.id,
        ).scalar()
        avg_score = float(avg_score_row) if avg_score_row else None

        # Assessment completion (assessments with a score vs total)
        total_assess = db.query(func.count()).filter(Assessment.student_id == student.id).scalar() or 0
        scored_assess = db.query(func.count()).filter(
            Assessment.student_id == student.id, Assessment.score.isnot(None),
        ).scalar() or 0
        completion_pct = (scored_assess / total_assess * 100) if total_assess > 0 else None

        # Failed assessments (score < 50%)
        failed = db.query(func.count()).filter(
            Assessment.student_id == student.id,
            Assessment.score < 50,
        ).scalar() or 0
        fail_pct = (failed / total_assess * 100) if total_assess > 0 else None

        # GPA trend (simple: compare to institution average)
        gpa = float(student.current_gpa) if student.current_gpa else None
        gpa_trend = "stable"
        if gpa is not None:
            # Get program for this student
            enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.id
            ).first()
            if enrollment and enrollment.program_id in program_avgs:
                prog_avg = program_avgs[enrollment.program_id]
                if prog_avg and gpa > prog_avg + 0.3:
                    gpa_trend = "improving"
                elif prog_avg and gpa < prog_avg - 0.5:
                    gpa_trend = "declining"

        # Program average for performance risk
        prog_avg = None
        enrollment = db.query(Enrollment).filter(Enrollment.student_id == student.id).first()
        if enrollment:
            prog_avg = program_avgs.get(enrollment.program_id)

        # Compute scores
        dropout_risk = compute_dropout_risk(
            attendance_rate, gpa, completion_pct,
            student.current_semester, gpa_trend,
        )
        perf_risk = compute_performance_risk(
            gpa, prog_avg, avg_score, attendance_rate, fail_pct,
        )

        risk_factors = json.dumps({
            "attendance_rate": round(attendance_rate, 1) if attendance_rate else None,
            "gpa": gpa,
            "assessment_completion": round(completion_pct, 1) if completion_pct else None,
            "semester": student.current_semester,
            "gpa_trend": gpa_trend,
            "failed_assessments_pct": round(fail_pct, 1) if fail_pct else None,
        })

        # Upsert analytics score
        existing = db.query(AnalyticsStudentScore).filter(
            AnalyticsStudentScore.student_id == student.id,
        ).first()

        if existing:
            existing.dropout_risk = dropout_risk
            existing.performance_risk = perf_risk
            existing.attendance_rate = attendance_rate
            existing.avg_score = avg_score
            existing.gpa_trend = gpa_trend
            existing.risk_factors = risk_factors
            existing.computed_at = datetime.now(timezone.utc)
        else:
            score = AnalyticsStudentScore(
                student_id=student.id,
                institution_id=inst_uuid,
                dropout_risk=dropout_risk,
                performance_risk=perf_risk,
                attendance_rate=attendance_rate,
                avg_score=avg_score,
                gpa_trend=gpa_trend,
                risk_factors=risk_factors,
            )
            db.add(score)

    db.commit()
    logger.info(f"Student scores computed for {institution_id}")


def compute_program_scores(db: Session, institution_id: str):
    """Compute program performance and relevance scores."""
    inst_uuid = institution_id
    programs = db.query(Program).filter(Program.institution_id == inst_uuid).all()

    for program in programs:
        # Completion rate
        total_enrolled = db.query(func.count()).filter(
            Enrollment.program_id == program.id,
        ).scalar() or 0
        completed = db.query(func.count()).filter(
            Enrollment.program_id == program.id, Enrollment.status == "completed",
        ).scalar() or 0
        completion_rate = (completed / total_enrolled * 100) if total_enrolled > 0 else None

        # Pass rate (students with GPA >= 2.0)
        active_students = db.query(func.count()).filter(
            Enrollment.program_id == program.id,
            Enrollment.status.in_(["active", "completed"]),
        ).scalar() or 0
        passing = (
            db.query(func.count())
            .select_from(Student)
            .join(Enrollment, Enrollment.student_id == Student.id)
            .filter(
                Enrollment.program_id == program.id,
                Student.current_gpa >= 2.0,
            )
            .scalar() or 0
        )
        pass_rate = (passing / active_students * 100) if active_students > 0 else None

        # Average GPA
        avg_gpa = (
            db.query(func.avg(Student.current_gpa))
            .join(Enrollment, Enrollment.student_id == Student.id)
            .filter(Enrollment.program_id == program.id, Student.is_active == True)
            .scalar()
        )
        avg_gpa = float(avg_gpa) if avg_gpa else None

        # Dropout rate
        dropped = db.query(func.count()).filter(
            Enrollment.program_id == program.id, Enrollment.status == "dropped",
        ).scalar() or 0
        dropout_rate = (dropped / total_enrolled * 100) if total_enrolled > 0 else None

        # Enrollment trend (simple heuristic based on name/code)
        market_data = PROGRAM_MARKET_DATA.get(program.name) or PROGRAM_MARKET_DATA.get(program.code) or {}
        growth = market_data.get("growth", 0)
        if growth > 10:
            enrollment_trend = "growing"
        elif growth < 0:
            enrollment_trend = "declining"
        else:
            enrollment_trend = "stable"

        # Relevance score
        relevance = compute_relevance_score(
            market_data.get("skills_overlap"),
            market_data.get("growth"),
            market_data.get("demand"),
        )

        # Program performance score
        perf_score = compute_program_score(
            completion_rate, avg_gpa, pass_rate, relevance, enrollment_trend,
        )

        demand_trend = enrollment_trend

        # Upsert
        existing = db.query(AnalyticsProgramScore).filter(
            AnalyticsProgramScore.program_id == program.id,
        ).first()

        if existing:
            existing.performance_score = perf_score
            existing.completion_rate = completion_rate
            existing.pass_rate = pass_rate
            existing.avg_gpa = avg_gpa
            existing.dropout_rate = dropout_rate
            existing.enrollment_trend = enrollment_trend
            existing.relevance_score = relevance
            existing.demand_trend = demand_trend
            existing.computed_at = datetime.now(timezone.utc)
        else:
            ps = AnalyticsProgramScore(
                program_id=program.id,
                institution_id=inst_uuid,
                performance_score=perf_score,
                completion_rate=completion_rate,
                pass_rate=pass_rate,
                avg_gpa=avg_gpa,
                dropout_rate=dropout_rate,
                enrollment_trend=enrollment_trend,
                relevance_score=relevance,
                demand_trend=demand_trend,
            )
            db.add(ps)

    db.commit()
    logger.info(f"Program scores computed for {institution_id}")


def compute_institution_kpis(db: Session, institution_id: str):
    """Compute and cache institution-level KPIs."""
    inst_uuid = institution_id

    total = db.query(func.count()).filter(Student.institution_id == inst_uuid).scalar() or 0
    active = db.query(func.count()).filter(Student.institution_id == inst_uuid, Student.is_active == True).scalar() or 0
    programs_count = db.query(func.count()).filter(Program.institution_id == inst_uuid).scalar() or 0
    avg_gpa = db.query(func.avg(Student.current_gpa)).filter(
        Student.institution_id == inst_uuid, Student.is_active == True,
    ).scalar()

    # Attendance
    total_att = db.query(func.count()).filter(AttendanceRecord.institution_id == inst_uuid).scalar() or 0
    present_att = db.query(func.count()).filter(
        AttendanceRecord.institution_id == inst_uuid,
        AttendanceRecord.status.in_(["present", "late"]),
    ).scalar() or 0
    overall_attendance = (present_att / total_att * 100) if total_att > 0 else None

    # Pass rate
    active_with_gpa = db.query(func.count()).filter(
        Student.institution_id == inst_uuid, Student.is_active == True, Student.current_gpa.isnot(None),
    ).scalar() or 0
    passing = db.query(func.count()).filter(
        Student.institution_id == inst_uuid, Student.is_active == True, Student.current_gpa >= 2.0,
    ).scalar() or 0
    overall_pass_rate = (passing / active_with_gpa * 100) if active_with_gpa > 0 else None

    # Dropout rate
    total_enrolled = db.query(func.count()).filter(Enrollment.institution_id == inst_uuid).scalar() or 0
    dropped = db.query(func.count()).filter(
        Enrollment.institution_id == inst_uuid, Enrollment.status == "dropped",
    ).scalar() or 0
    overall_dropout_rate = (dropped / total_enrolled * 100) if total_enrolled > 0 else None

    # Risk counts
    at_risk = db.query(func.count()).filter(
        AnalyticsStudentScore.institution_id == inst_uuid,
        AnalyticsStudentScore.dropout_risk >= 40,
    ).scalar() or 0
    high_risk = db.query(func.count()).filter(
        AnalyticsStudentScore.institution_id == inst_uuid,
        AnalyticsStudentScore.dropout_risk >= 70,
    ).scalar() or 0

    # Program averages
    avg_prog_score = db.query(func.avg(AnalyticsProgramScore.performance_score)).filter(
        AnalyticsProgramScore.institution_id == inst_uuid,
    ).scalar()
    avg_relevance = db.query(func.avg(AnalyticsProgramScore.relevance_score)).filter(
        AnalyticsProgramScore.institution_id == inst_uuid,
    ).scalar()

    # Upsert for period="latest"
    existing = db.query(AnalyticsInstitutionKPI).filter(
        AnalyticsInstitutionKPI.institution_id == inst_uuid,
        AnalyticsInstitutionKPI.period == "latest",
    ).first()

    kpi_data = dict(
        total_students=total,
        active_students=active,
        total_programs=programs_count,
        avg_gpa=round(float(avg_gpa), 2) if avg_gpa else None,
        overall_attendance=round(overall_attendance, 1) if overall_attendance else None,
        overall_pass_rate=round(overall_pass_rate, 1) if overall_pass_rate else None,
        overall_dropout_rate=round(overall_dropout_rate, 1) if overall_dropout_rate else None,
        at_risk_students=at_risk,
        high_risk_students=high_risk,
        avg_program_score=round(float(avg_prog_score), 1) if avg_prog_score else None,
        avg_relevance_score=round(float(avg_relevance), 1) if avg_relevance else None,
        computed_at=datetime.now(timezone.utc),
    )

    if existing:
        for k, v in kpi_data.items():
            setattr(existing, k, v)
    else:
        kpi = AnalyticsInstitutionKPI(institution_id=inst_uuid, period="latest", **kpi_data)
        db.add(kpi)

    db.commit()
    logger.info(f"Institution KPIs computed for {institution_id}")
