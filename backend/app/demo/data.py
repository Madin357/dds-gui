"""
In-memory demo data for both institutions.
Generated at import time with a fixed seed for consistency.
"""

import random
import uuid
from datetime import date, datetime, timedelta, timezone

random.seed(42)

_INST_UNI = "demo-uni-001"
_INST_PROV = "demo-prov-001"

# --- Helpers ---

_FIRST_M = ["Elvin", "Farid", "Kamran", "Orkhan", "Rashad", "Tural", "Vugar", "Zaur", "Nihad", "Samir", "Emil", "Ramin", "Javid", "Murad"]
_FIRST_F = ["Aysel", "Gunel", "Leyla", "Narmin", "Sabina", "Turana", "Vusala", "Zeynab", "Nigar", "Samira", "Emilia", "Rana", "Nargiz", "Irada"]
_LAST = ["Mammadov", "Aliyev", "Hasanov", "Huseynov", "Guliyev", "Rzayev", "Bayramov", "Ismayilov", "Abbasov", "Musayev", "Karimov", "Ibrahimov", "Hajiyev", "Ahmadov"]


def _uid():
    return str(uuid.uuid4())


def _name():
    g = random.choice(["M", "F"])
    fn = random.choice(_FIRST_M if g == "M" else _FIRST_F)
    ln = random.choice(_LAST)
    if g == "F" and not ln.endswith("a"):
        ln += "a"
    return fn, ln, g


# =====================================================================
# UNIVERSITY DATA
# =====================================================================

UNI_PROGRAMS = [
    {"id": _uid(), "name": "Computer Science", "code": "CS", "level": "bachelor", "department": "Faculty of IT", "duration_months": 48, "is_active": True,
     "performance_score": 78.5, "completion_rate": 82.0, "pass_rate": 80.0, "avg_gpa": 77.5, "dropout_rate": 10.0, "enrollment_trend": "growing", "relevance_score": 85.0, "demand_trend": "growing", "student_count": 35},
    {"id": _uid(), "name": "Business Administration", "code": "BA", "level": "bachelor", "department": "Faculty of Economics", "duration_months": 48, "is_active": True,
     "performance_score": 65.2, "completion_rate": 74.0, "pass_rate": 72.0, "avg_gpa": 72.5, "dropout_rate": 12.0, "enrollment_trend": "stable", "relevance_score": 55.0, "demand_trend": "stable", "student_count": 28},
    {"id": _uid(), "name": "Civil Engineering", "code": "CE", "level": "bachelor", "department": "Faculty of Engineering", "duration_months": 48, "is_active": True,
     "performance_score": 60.8, "completion_rate": 70.0, "pass_rate": 68.0, "avg_gpa": 67.5, "dropout_rate": 14.0, "enrollment_trend": "stable", "relevance_score": 58.0, "demand_trend": "stable", "student_count": 22},
    {"id": _uid(), "name": "Medicine", "code": "MED", "level": "bachelor", "department": "Faculty of Medicine", "duration_months": 72, "is_active": True,
     "performance_score": 82.0, "completion_rate": 90.0, "pass_rate": 88.0, "avg_gpa": 82.5, "dropout_rate": 5.0, "enrollment_trend": "stable", "relevance_score": 72.0, "demand_trend": "stable", "student_count": 20},
    {"id": _uid(), "name": "Azerbaijani Language & Literature", "code": "ALL", "level": "bachelor", "department": "Faculty of Humanities", "duration_months": 48, "is_active": True,
     "performance_score": 45.3, "completion_rate": 65.0, "pass_rate": 60.0, "avg_gpa": 70.0, "dropout_rate": 16.0, "enrollment_trend": "declining", "relevance_score": 22.0, "demand_trend": "declining", "student_count": 15},
]

UNI_COURSES = {}
_cs_courses = [("Introduction to Programming", "CS101", 1), ("Data Structures", "CS201", 2), ("Algorithms", "CS301", 3), ("Database Systems", "CS202", 2), ("Machine Learning", "CS401", 4)]
_ba_courses = [("Principles of Management", "BA101", 1), ("Microeconomics", "BA102", 1), ("Financial Accounting", "BA201", 2), ("Marketing", "BA202", 2)]
_ce_courses = [("Engineering Mathematics", "CE101", 1), ("Structural Analysis", "CE201", 2), ("Geotechnics", "CE301", 3), ("Construction Management", "CE302", 3)]
_med_courses = [("Anatomy", "MED101", 1), ("Physiology", "MED102", 1), ("Biochemistry", "MED201", 2), ("Pathology", "MED301", 3)]
_all_courses = [("Azerbaijani Grammar", "ALL101", 1), ("Classical Literature", "ALL102", 1), ("Linguistics", "ALL301", 3)]

for prog, courses_list in zip(UNI_PROGRAMS, [_cs_courses, _ba_courses, _ce_courses, _med_courses, _all_courses]):
    UNI_COURSES[prog["id"]] = [
        {"id": _uid(), "name": n, "code": c, "credits": 3.0, "semester": s, "program_name": prog["name"]}
        for n, c, s in courses_list
    ]


def _gen_students(programs, inst_id, code_prefix, email_domain, count_map):
    students = []
    idx = 0
    for prog, cnt in zip(programs, count_map):
        profile_gpa = prog["avg_gpa"] / 100 * 4
        for _ in range(cnt):
            idx += 1
            fn, ln, g = _name()
            sem = random.randint(1, 8)
            att = max(35, min(100, round(random.gauss(78, 12), 1)))
            gpa_raw = max(0.5, min(4.0, round(profile_gpa + random.gauss(0, 0.4), 2)))
            gpa_100 = round(gpa_raw / 4.0 * 100, 1)
            is_dropped = random.random() < prog["dropout_rate"] / 100
            dropout_risk = round(random.uniform(60, 90) if is_dropped else max(0, min(95, random.gauss(25, 18))), 2)
            perf_risk = round(max(0, min(95, random.gauss(30, 20))), 2)
            students.append({
                "id": _uid(), "student_code": f"{code_prefix}-{idx:04d}",
                "first_name": fn, "last_name": ln, "email": f"{fn.lower()}.{ln.lower()}@{email_domain}",
                "gender": g, "date_of_birth": f"{random.randint(1998, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                "enrollment_date": f"{2026 - (sem - 1) // 2 - 1}-09-{random.randint(1,15):02d}",
                "current_gpa": gpa_100, "current_semester": sem,
                "is_active": not is_dropped, "dropout_risk": dropout_risk, "performance_risk": perf_risk,
                "attendance_rate": att if not is_dropped else max(30, att - 20),
                "avg_score": round(gpa_100 + random.gauss(0, 5), 1),
                "gpa_trend": random.choice(["improving", "stable", "declining"]),
                "risk_factors": {"attendance_rate": att, "gpa": gpa_raw, "semester": sem, "gpa_trend": "stable"},
                "program_name": prog["name"], "program_id": prog["id"],
                "institution_id": inst_id,
            })
    return students


UNI_STUDENTS = _gen_students(UNI_PROGRAMS, _INST_UNI, "BEU", "beu.edu.az", [35, 28, 22, 20, 15])


def _gen_attendance(student):
    records = []
    courses = UNI_COURSES.get(student["program_id"]) or PROV_COURSES.get(student["program_id"]) or []
    for course in courses[:2]:
        for day_offset in range(0, 20, random.randint(3, 5)):
            d = date(2026, 2, 1) + timedelta(days=day_offset)
            if random.random() * 100 < (student["attendance_rate"] or 75):
                status = random.choices(["present", "late"], [90, 10])[0]
            else:
                status = random.choices(["absent", "excused"], [80, 20])[0]
            records.append({"id": _uid(), "course_name": course["name"], "session_date": d.isoformat(), "status": status})
    return records


def _gen_assessments(student):
    records = []
    courses = UNI_COURSES.get(student["program_id"]) or PROV_COURSES.get(student["program_id"]) or []
    for course in courses[:2]:
        for atype in ["midterm", "final"]:
            score = max(15, min(100, round((student["current_gpa"] or 70) + random.gauss(0, 10), 1)))
            grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"
            month = 2 if atype == "midterm" else 4
            records.append({
                "id": _uid(), "course_name": course["name"], "type": atype, "title": f"{atype.title()} Exam",
                "score": score, "max_score": 100, "percentage": score, "grade": grade,
                "assessed_at": f"2026-{month:02d}-{random.randint(5, 25):02d}",
            })
    return records


# =====================================================================
# COURSE PROVIDER DATA
# =====================================================================

PROV_PROGRAMS = [
    {"id": _uid(), "name": "Web Development Bootcamp", "code": "WEB", "level": "bootcamp", "department": "Technology", "duration_months": 4, "is_active": True,
     "performance_score": 74.0, "completion_rate": 80.0, "pass_rate": 78.0, "avg_gpa": 72.0, "dropout_rate": 12.0, "enrollment_trend": "growing", "relevance_score": 82.0, "demand_trend": "growing", "student_count": 14},
    {"id": _uid(), "name": "Data Science Fundamentals", "code": "DS", "level": "course", "department": "Technology", "duration_months": 5, "is_active": True,
     "performance_score": 70.5, "completion_rate": 75.0, "pass_rate": 74.0, "avg_gpa": 68.0, "dropout_rate": 15.0, "enrollment_trend": "growing", "relevance_score": 88.0, "demand_trend": "growing", "student_count": 16},
    {"id": _uid(), "name": "Digital Marketing", "code": "DM", "level": "course", "department": "Business", "duration_months": 3, "is_active": True,
     "performance_score": 62.0, "completion_rate": 70.0, "pass_rate": 68.0, "avg_gpa": 70.0, "dropout_rate": 18.0, "enrollment_trend": "stable", "relevance_score": 55.0, "demand_trend": "stable", "student_count": 10},
    {"id": _uid(), "name": "UI/UX Design", "code": "UX", "level": "course", "department": "Design", "duration_months": 3, "is_active": True,
     "performance_score": 72.0, "completion_rate": 78.0, "pass_rate": 76.0, "avg_gpa": 75.0, "dropout_rate": 10.0, "enrollment_trend": "growing", "relevance_score": 68.0, "demand_trend": "growing", "student_count": 8},
    {"id": _uid(), "name": "Cybersecurity Essentials", "code": "CYB", "level": "course", "department": "Technology", "duration_months": 4, "is_active": True,
     "performance_score": 68.0, "completion_rate": 72.0, "pass_rate": 70.0, "avg_gpa": 65.0, "dropout_rate": 14.0, "enrollment_trend": "growing", "relevance_score": 75.0, "demand_trend": "growing", "student_count": 8},
    {"id": _uid(), "name": "Cloud Computing", "code": "CLD", "level": "course", "department": "Technology", "duration_months": 3, "is_active": True,
     "performance_score": 66.0, "completion_rate": 74.0, "pass_rate": 72.0, "avg_gpa": 67.0, "dropout_rate": 12.0, "enrollment_trend": "growing", "relevance_score": 78.0, "demand_trend": "growing", "student_count": 8},
    {"id": _uid(), "name": "Project Management", "code": "PM", "level": "course", "department": "Business", "duration_months": 2, "is_active": True,
     "performance_score": 55.0, "completion_rate": 60.0, "pass_rate": 58.0, "avg_gpa": 65.0, "dropout_rate": 22.0, "enrollment_trend": "declining", "relevance_score": 45.0, "demand_trend": "stable", "student_count": 6},
    {"id": _uid(), "name": "AI & Machine Learning", "code": "AIML", "level": "course", "department": "Technology", "duration_months": 5, "is_active": True,
     "performance_score": 71.0, "completion_rate": 70.0, "pass_rate": 68.0, "avg_gpa": 66.0, "dropout_rate": 16.0, "enrollment_trend": "growing", "relevance_score": 90.0, "demand_trend": "growing", "student_count": 12},
]

PROV_COURSES = {}
_prov_course_defs = {
    0: [("HTML & CSS", "WEB-1", 1), ("JavaScript", "WEB-2", 2), ("React", "WEB-3", 3)],
    1: [("Python Basics", "DS-1", 1), ("Statistics", "DS-2", 2), ("ML Intro", "DS-3", 3)],
    2: [("Marketing Fundamentals", "DM-1", 1), ("Social Media", "DM-2", 2), ("SEO & SEM", "DM-3", 3)],
    3: [("Design Thinking", "UX-1", 1), ("Figma Workshop", "UX-2", 2), ("User Research", "UX-3", 3)],
    4: [("Network Security", "CYB-1", 1), ("Cryptography", "CYB-2", 2), ("Ethical Hacking", "CYB-3", 3)],
    5: [("Cloud Basics", "CLD-1", 1), ("AWS/Azure", "CLD-2", 2), ("DevOps", "CLD-3", 3)],
    6: [("PM Fundamentals", "PM-1", 1), ("Agile & Scrum", "PM-2", 2)],
    7: [("AI Foundations", "AIML-1", 1), ("Deep Learning", "AIML-2", 2), ("NLP", "AIML-3", 3)],
}
for i, prog in enumerate(PROV_PROGRAMS):
    PROV_COURSES[prog["id"]] = [
        {"id": _uid(), "name": n, "code": c, "credits": None, "semester": s, "program_name": prog["name"]}
        for n, c, s in _prov_course_defs[i]
    ]

PROV_STUDENTS = _gen_students(PROV_PROGRAMS, _INST_PROV, "ADA", "learn.az", [14, 16, 10, 8, 8, 8, 6, 12])


# =====================================================================
# SHARED: Labour market & skills
# =====================================================================

LABOUR_TRENDS = [
    {"id": _uid(), "occupation": "Software Developer", "sector": "Technology", "demand_level": "high", "growth_rate": 22.0, "avg_salary_azn": 2500, "job_postings": 450},
    {"id": _uid(), "occupation": "Data Analyst", "sector": "Technology", "demand_level": "high", "growth_rate": 30.0, "avg_salary_azn": 2200, "job_postings": 380},
    {"id": _uid(), "occupation": "Cybersecurity Specialist", "sector": "Technology", "demand_level": "high", "growth_rate": 25.0, "avg_salary_azn": 2800, "job_postings": 220},
    {"id": _uid(), "occupation": "Cloud Engineer", "sector": "Technology", "demand_level": "high", "growth_rate": 28.0, "avg_salary_azn": 3000, "job_postings": 180},
    {"id": _uid(), "occupation": "AI/ML Engineer", "sector": "Technology", "demand_level": "high", "growth_rate": 35.0, "avg_salary_azn": 3500, "job_postings": 150},
    {"id": _uid(), "occupation": "Digital Marketing Specialist", "sector": "Business", "demand_level": "medium", "growth_rate": 5.0, "avg_salary_azn": 1500, "job_postings": 300},
    {"id": _uid(), "occupation": "Civil Engineer", "sector": "Engineering", "demand_level": "medium", "growth_rate": 8.0, "avg_salary_azn": 2000, "job_postings": 250},
    {"id": _uid(), "occupation": "Project Manager", "sector": "Business", "demand_level": "medium", "growth_rate": 6.0, "avg_salary_azn": 2200, "job_postings": 200},
    {"id": _uid(), "occupation": "Medical Doctor", "sector": "Healthcare", "demand_level": "high", "growth_rate": 12.0, "avg_salary_azn": 3000, "job_postings": 180},
    {"id": _uid(), "occupation": "UI/UX Designer", "sector": "Design", "demand_level": "high", "growth_rate": 15.0, "avg_salary_azn": 2000, "job_postings": 160},
    {"id": _uid(), "occupation": "Web Developer", "sector": "Technology", "demand_level": "high", "growth_rate": 18.0, "avg_salary_azn": 2200, "job_postings": 400},
    {"id": _uid(), "occupation": "DevOps Engineer", "sector": "Technology", "demand_level": "high", "growth_rate": 28.0, "avg_salary_azn": 2800, "job_postings": 170},
]

SKILL_TRENDS = [
    {"id": _uid(), "skill_name": "Python", "category": "technical", "demand_level": "high", "growth_rate": 30.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "SQL", "category": "technical", "demand_level": "high", "growth_rate": 15.0, "future_outlook": "stable"},
    {"id": _uid(), "skill_name": "JavaScript", "category": "technical", "demand_level": "high", "growth_rate": 12.0, "future_outlook": "stable"},
    {"id": _uid(), "skill_name": "React", "category": "technical", "demand_level": "high", "growth_rate": 18.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "Machine Learning", "category": "technical", "demand_level": "emerging", "growth_rate": 35.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "Cloud Platforms (AWS/Azure)", "category": "technical", "demand_level": "high", "growth_rate": 28.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "Data Visualization", "category": "technical", "demand_level": "high", "growth_rate": 20.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "Cybersecurity", "category": "technical", "demand_level": "high", "growth_rate": 25.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "Project Management", "category": "soft", "demand_level": "medium", "growth_rate": 6.0, "future_outlook": "stable"},
    {"id": _uid(), "skill_name": "Communication", "category": "soft", "demand_level": "medium", "growth_rate": 3.0, "future_outlook": "stable"},
    {"id": _uid(), "skill_name": "UX Research", "category": "technical", "demand_level": "emerging", "growth_rate": 15.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "DevOps/CI-CD", "category": "technical", "demand_level": "high", "growth_rate": 28.0, "future_outlook": "growing"},
    {"id": _uid(), "skill_name": "NLP", "category": "technical", "demand_level": "emerging", "growth_rate": 32.0, "future_outlook": "growing"},
]


# =====================================================================
# RECOMMENDATIONS
# =====================================================================

_now = datetime.now(timezone.utc).isoformat()

UNI_RECOMMENDATIONS = [
    {"id": _uid(), "level": "institution", "target_id": None, "category": "new_program", "title": "Launch Data Science Specialization",
     "description": "Market demand for data science skills is growing 30% YoY. Your Computer Science program already covers 60% of prerequisite skills.", "ai_generated": True, "priority_score": 92.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "program", "target_id": None, "category": "curriculum", "title": "Update Language & Literature Program",
     "description": "Enrollment is declining 10% YoY and labour market demand for traditional language skills is low. Consider adding digital content creation modules.", "ai_generated": True, "priority_score": 78.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "institution", "target_id": None, "category": "intervention", "title": "Implement First-Year Early Warning System",
     "description": "15% of first-year students are dropping out. Targeted mentoring for students with attendance below 75% could reduce dropout by 30-40%.", "ai_generated": True, "priority_score": 85.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "program", "target_id": None, "category": "resource", "title": "Increase Engineering Lab Capacity",
     "description": "Civil Engineering has the lowest average scores. Student feedback indicates insufficient lab time.", "ai_generated": False, "priority_score": 65.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "institution", "target_id": None, "category": "policy", "title": "Attendance-Linked Academic Support",
     "description": "Students with attendance below 70% have GPAs 1.5 points lower on average. Automatic referral to academic support is recommended.", "ai_generated": True, "priority_score": 80.0, "status": "active", "data_snapshot": None, "created_at": _now},
]

PROV_RECOMMENDATIONS = [
    {"id": _uid(), "level": "institution", "target_id": None, "category": "new_program", "title": "Add Cybersecurity Advanced Track",
     "description": "Cybersecurity demand is surging (+25% growth). An advanced track covering penetration testing would fill a critical market gap.", "ai_generated": True, "priority_score": 88.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "program", "target_id": None, "category": "curriculum", "title": "Refresh Project Management Curriculum",
     "description": "PM program has the lowest completion rate (60%). Consider adding Agile certifications prep and real-world case studies.", "ai_generated": True, "priority_score": 72.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "institution", "target_id": None, "category": "intervention", "title": "First-Month Onboarding Enhancement",
     "description": "20% of students drop out in the first month. A structured onboarding week with mentoring could significantly reduce early dropout.", "ai_generated": True, "priority_score": 90.0, "status": "active", "data_snapshot": None, "created_at": _now},
    {"id": _uid(), "level": "program", "target_id": None, "category": "new_program", "title": "Launch Cloud & DevOps Bootcamp",
     "description": "Cloud/DevOps skills are growing 28% YoY with very few local training options. A full bootcamp would meet unserved demand.", "ai_generated": True, "priority_score": 85.0, "status": "active", "data_snapshot": None, "created_at": _now},
]


# =====================================================================
# Dashboard KPIs (pre-computed)
# =====================================================================

def _compute_kpis(students, programs):
    active = [s for s in students if s["is_active"]]
    at_risk = [s for s in students if s["dropout_risk"] and s["dropout_risk"] >= 40]
    high_risk = [s for s in students if s["dropout_risk"] and s["dropout_risk"] >= 70]
    avg_gpa = round(sum(s["current_gpa"] for s in active if s["current_gpa"]) / max(len(active), 1), 1)
    avg_att = round(sum(s["attendance_rate"] for s in active if s["attendance_rate"]) / max(len(active), 1), 1)
    pass_count = sum(1 for s in active if s["current_gpa"] and s["current_gpa"] >= 77.5)
    pass_rate = round(pass_count / max(len(active), 1) * 100, 1)
    dropped = sum(1 for s in students if not s["is_active"])
    dropout_rate = round(dropped / max(len(students), 1) * 100, 1)
    avg_prog = round(sum(p["performance_score"] for p in programs) / max(len(programs), 1), 1)
    avg_rel = round(sum(p["relevance_score"] for p in programs) / max(len(programs), 1), 1)
    return {
        "total_students": len(students), "active_students": len(active), "total_programs": len(programs),
        "avg_gpa": avg_gpa, "overall_attendance": avg_att, "overall_pass_rate": pass_rate,
        "overall_dropout_rate": dropout_rate, "at_risk_students": len(at_risk), "high_risk_students": len(high_risk),
        "avg_program_score": avg_prog, "avg_relevance_score": avg_rel,
    }


def _risk_dist(students):
    high = sum(1 for s in students if s["dropout_risk"] and s["dropout_risk"] >= 70)
    med = sum(1 for s in students if s["dropout_risk"] and 40 <= s["dropout_risk"] < 70)
    low = sum(1 for s in students if s["dropout_risk"] and s["dropout_risk"] < 40)
    return {"high": high, "medium": med, "low": low}


UNI_KPIS = _compute_kpis(UNI_STUDENTS, UNI_PROGRAMS)
PROV_KPIS = _compute_kpis(PROV_STUDENTS, PROV_PROGRAMS)


# =====================================================================
# Lookup helpers
# =====================================================================

DEMO_USERS = {
    "admin@beu.edu.az": {
        "id": "demo-user-uni-001", "email": "admin@beu.edu.az", "password": "demo123",
        "full_name": "BEU Admin", "role": "admin", "institution_id": _INST_UNI, "institution_name": "Baku Engineering University",
    },
    "admin@digitalacademy.az": {
        "id": "demo-user-prov-001", "email": "admin@digitalacademy.az", "password": "demo123",
        "full_name": "ADA Admin", "role": "admin", "institution_id": _INST_PROV, "institution_name": "Azerbaijan Digital Academy",
    },
}

_DATA = {
    _INST_UNI: {"programs": UNI_PROGRAMS, "courses": UNI_COURSES, "students": UNI_STUDENTS, "kpis": UNI_KPIS, "recommendations": UNI_RECOMMENDATIONS},
    _INST_PROV: {"programs": PROV_PROGRAMS, "courses": PROV_COURSES, "students": PROV_STUDENTS, "kpis": PROV_KPIS, "recommendations": PROV_RECOMMENDATIONS},
}


def get_institution_data(institution_id: str) -> dict:
    return _DATA.get(institution_id, _DATA[_INST_UNI])
