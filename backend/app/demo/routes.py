"""
Demo-mode API routes. Serves in-memory mock data — no database required.
Matches the exact API contract that the frontend expects.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.config import get_settings
from app.demo.data import (
    DEMO_USERS, LABOUR_TRENDS, SKILL_TRENDS,
    get_institution_data, _risk_dist,
    _gen_attendance, _gen_assessments,
)

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --- Request models (ensures FastAPI parses JSON body correctly) ---

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TriggerSyncRequest(BaseModel):
    sync_type: str = "incremental"

class UpdateStatusRequest(BaseModel):
    status: str


# --- Auth helpers ---

def _create_token(user_id: str, institution_id: str, token_type: str, minutes: int) -> str:
    payload = {"sub": user_id, "inst": institution_id, "type": token_type,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _get_demo_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if payload.get("type") != "access" or not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    for u in DEMO_USERS.values():
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=401, detail="User not found")


# --- Routers ---

auth_router = APIRouter(prefix="/auth", tags=["auth"])
students_router = APIRouter(prefix="/students", tags=["students"])
programs_router = APIRouter(prefix="/programs", tags=["programs"])
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])
recommendations_router = APIRouter(tags=["recommendations"])
sync_router = APIRouter(prefix="/sync", tags=["sync"])


# ===================== AUTH =====================

@auth_router.post("/login")
async def demo_login(req: LoginRequest):
    user = DEMO_USERS.get(req.email)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": _create_token(user["id"], user["institution_id"], "access", 120),
        "refresh_token": _create_token(user["id"], user["institution_id"], "refresh", 10080),
        "token_type": "bearer",
    }


@auth_router.post("/refresh")
async def demo_refresh(req: RefreshRequest):
    try:
        payload = jwt.decode(req.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["sub"]
        inst_id = payload["inst"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {
        "access_token": _create_token(user_id, inst_id, "access", 120),
        "refresh_token": _create_token(user_id, inst_id, "refresh", 10080),
        "token_type": "bearer",
    }


@auth_router.get("/me")
async def demo_me(user: dict = Depends(_get_demo_user)):
    return {k: v for k, v in user.items() if k != "password"}


# ===================== ANALYTICS =====================

@analytics_router.get("/dashboard")
async def demo_dashboard(user: dict = Depends(_get_demo_user)):
    data = get_institution_data(user["institution_id"])
    kpis = data["kpis"]
    students = data["students"]
    programs = data["programs"]
    recs = data["recommendations"]

    enrollment_trend = []
    for year in range(2021, 2027):
        enrollment_trend.append({"period": str(year), "count": len(students) // 6 + (year - 2020) * 3})

    return {
        "kpis": kpis,
        "enrollment_trend": enrollment_trend,
        "risk_distribution": _risk_dist(students),
        "top_programs": [{"name": p["name"], "performance_score": p["performance_score"], "completion_rate": p["completion_rate"]} for p in programs],
        "recent_recommendations": [{"id": r["id"], "title": r["title"], "category": r["category"], "level": r["level"], "priority_score": r["priority_score"]} for r in recs[:5]],
    }


@analytics_router.get("/kpis")
async def demo_kpis(user: dict = Depends(_get_demo_user)):
    return get_institution_data(user["institution_id"])["kpis"]


# ===================== STUDENTS =====================

@students_router.get("")
async def demo_list_students(
    user: dict = Depends(_get_demo_user),
    page: int = 1, page_size: int = 20,
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    program_id: Optional[str] = None,
    status: Optional[str] = None,
):
    students = get_institution_data(user["institution_id"])["students"]
    filtered = list(students)
    if search:
        q = search.lower()
        filtered = [s for s in filtered if q in s["first_name"].lower() or q in s["last_name"].lower() or q in (s["student_code"] or "").lower()]
    if risk_level == "high":
        filtered = [s for s in filtered if s["dropout_risk"] and s["dropout_risk"] >= 70]
    elif risk_level == "medium":
        filtered = [s for s in filtered if s["dropout_risk"] and 40 <= s["dropout_risk"] < 70]
    elif risk_level == "low":
        filtered = [s for s in filtered if s["dropout_risk"] and s["dropout_risk"] < 40]
    if program_id:
        filtered = [s for s in filtered if s.get("program_id") == program_id]
    if status == "active":
        filtered = [s for s in filtered if s["is_active"]]
    elif status == "dropped":
        filtered = [s for s in filtered if not s["is_active"]]

    total = len(filtered)
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@students_router.get("/at-risk")
async def demo_at_risk(user: dict = Depends(_get_demo_user), limit: int = 20):
    students = get_institution_data(user["institution_id"])["students"]
    at_risk = sorted([s for s in students if s["dropout_risk"] and s["dropout_risk"] >= 40], key=lambda s: -s["dropout_risk"])
    return at_risk[:limit]


@students_router.get("/{student_id}")
async def demo_student_detail(student_id: str, user: dict = Depends(_get_demo_user)):
    students = get_institution_data(user["institution_id"])["students"]
    for s in students:
        if s["id"] == student_id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")


@students_router.get("/{student_id}/attendance")
async def demo_student_attendance(student_id: str, user: dict = Depends(_get_demo_user)):
    students = get_institution_data(user["institution_id"])["students"]
    for s in students:
        if s["id"] == student_id:
            return _gen_attendance(s)
    return []


@students_router.get("/{student_id}/assessments")
async def demo_student_assessments(student_id: str, user: dict = Depends(_get_demo_user)):
    students = get_institution_data(user["institution_id"])["students"]
    for s in students:
        if s["id"] == student_id:
            return _gen_assessments(s)
    return []


# ===================== PROGRAMS =====================

@programs_router.get("")
async def demo_list_programs(user: dict = Depends(_get_demo_user)):
    programs = get_institution_data(user["institution_id"])["programs"]
    return {"items": programs, "total": len(programs)}


@programs_router.get("/comparison")
async def demo_comparison(user: dict = Depends(_get_demo_user)):
    programs = get_institution_data(user["institution_id"])["programs"]
    return [{"id": p["id"], "name": p["name"], "code": p["code"], "performance_score": p["performance_score"],
             "completion_rate": p["completion_rate"], "pass_rate": p["pass_rate"], "avg_gpa": p["avg_gpa"],
             "dropout_rate": p["dropout_rate"], "enrollment_trend": p["enrollment_trend"], "relevance_score": p["relevance_score"]}
            for p in programs]


@programs_router.get("/{program_id}")
async def demo_program_detail(program_id: str, user: dict = Depends(_get_demo_user)):
    programs = get_institution_data(user["institution_id"])["programs"]
    for p in programs:
        if p["id"] == program_id:
            return p
    raise HTTPException(status_code=404, detail="Program not found")


@programs_router.get("/{program_id}/courses")
async def demo_program_courses(program_id: str, user: dict = Depends(_get_demo_user)):
    courses = get_institution_data(user["institution_id"])["courses"]
    return courses.get(program_id, [])


# ===================== RECOMMENDATIONS & MARKET =====================

@recommendations_router.get("/recommendations")
async def demo_list_recommendations(
    user: dict = Depends(_get_demo_user),
    level: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = Query("active"),
):
    recs = get_institution_data(user["institution_id"])["recommendations"]
    filtered = list(recs)
    if level:
        filtered = [r for r in filtered if r["level"] == level]
    if category:
        filtered = [r for r in filtered if r["category"] == category]
    if status:
        filtered = [r for r in filtered if r["status"] == status]
    return {"items": filtered, "total": len(filtered)}


@recommendations_router.get("/recommendations/{rec_id}")
async def demo_get_recommendation(rec_id: str, user: dict = Depends(_get_demo_user)):
    recs = get_institution_data(user["institution_id"])["recommendations"]
    for r in recs:
        if r["id"] == rec_id:
            return r
    raise HTTPException(status_code=404, detail="Recommendation not found")


@recommendations_router.put("/recommendations/{rec_id}/status")
async def demo_update_rec_status(rec_id: str, req: UpdateStatusRequest, user: dict = Depends(_get_demo_user)):
    return {"message": "Status updated", "new_status": req.status}


@recommendations_router.get("/labour-market/trends")
async def demo_labour_trends(user: dict = Depends(_get_demo_user)):
    return LABOUR_TRENDS


@recommendations_router.get("/labour-market/skills")
async def demo_skill_trends(user: dict = Depends(_get_demo_user)):
    return SKILL_TRENDS


@recommendations_router.get("/labour-market/alignment")
async def demo_alignment(user: dict = Depends(_get_demo_user)):
    programs = get_institution_data(user["institution_id"])["programs"]
    return [{"name": p["name"], "code": p["code"], "relevance_score": p["relevance_score"], "demand_trend": p["demand_trend"]} for p in programs]


# ===================== SYNC (stub) =====================

@sync_router.get("/jobs")
async def demo_sync_jobs(user: dict = Depends(_get_demo_user)):
    return [{"id": "demo-sync-001", "name": "Demo Data Source", "source_type": "sqlite",
             "is_active": True, "schedule_cron": "*/15 * * * *",
             "tables_to_sync": ["programs", "courses", "students", "enrollments", "attendance", "assessments"],
             "created_at": datetime.now(timezone.utc).isoformat()}]


@sync_router.get("/jobs/{job_id}/runs")
async def demo_sync_runs(job_id: str, user: dict = Depends(_get_demo_user)):
    return [{"id": "demo-run-001", "sync_job_id": job_id, "status": "completed", "sync_type": "full",
             "started_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
             "completed_at": datetime.now(timezone.utc).isoformat(),
             "records_synced": 202, "records_failed": 0, "error_summary": None, "duration_ms": 3200}]


@sync_router.post("/jobs/{job_id}/trigger")
async def demo_trigger_sync(job_id: str, req: TriggerSyncRequest, user: dict = Depends(_get_demo_user)):
    return {"message": f"Sync triggered ({req.sync_type})"}


@sync_router.get("/status")
async def demo_sync_status(user: dict = Depends(_get_demo_user)):
    return {
        "total_jobs": 1, "active_jobs": 1,
        "last_sync": {"id": "demo-run-001", "sync_job_id": "demo-sync-001", "status": "completed", "sync_type": "full",
                       "started_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                       "completed_at": datetime.now(timezone.utc).isoformat(),
                       "records_synced": 202, "records_failed": 0, "error_summary": None, "duration_ms": 3200},
        "recent_errors": 0,
    }


@sync_router.get("/errors")
async def demo_sync_errors(user: dict = Depends(_get_demo_user)):
    return []


# ===================== Mount =====================

def mount_demo_routes(app: FastAPI):
    """Mount all demo routes on the app under /api/v1."""
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")
    app.include_router(students_router, prefix="/api/v1")
    app.include_router(programs_router, prefix="/api/v1")
    app.include_router(recommendations_router, prefix="/api/v1")
    app.include_router(sync_router, prefix="/api/v1")
