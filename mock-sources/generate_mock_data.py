"""
Generate realistic mock data for two institution types:
  1. Baku Engineering University (university)
  2. Azerbaijan Digital Academy (course provider)

Data patterns implemented:
  - CS enrollment growing, Language & Literature declining
  - First-year dropout ~15%, fourth-year ~2%
  - Attendance-performance correlation (low attendance → low GPA)
  - Engineering high difficulty / lower scores
  - Medicine high completion / strict attendance
  - Course provider: high first-month dropout, tech courses strong
"""

import sqlite3
import random
import os
from datetime import date, datetime, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Azerbaijani names
FIRST_NAMES_M = [
    "Elvin", "Farid", "Kamran", "Orkhan", "Rashad", "Tural", "Vugar", "Zaur",
    "Nihad", "Samir", "Emil", "Ramin", "Javid", "Murad", "Ilkin", "Nurlan",
    "Rovshan", "Anar", "Elchin", "Babek", "Rufat", "Togrul", "Namig", "Shahin",
    "Ayaz", "Kamal", "Huseyn", "Mahir", "Elmar", "Fuad",
]
FIRST_NAMES_F = [
    "Aysel", "Gunel", "Leyla", "Narmin", "Sabina", "Turana", "Vusala", "Zeynab",
    "Nigar", "Samira", "Emilia", "Rana", "Javida", "Nargiz", "Irada", "Nurana",
    "Roya", "Aynur", "Elnara", "Gulnara", "Rufana", "Tarana", "Narmina", "Shahla",
    "Aydan", "Kamala", "Lamiya", "Matanat", "Elmira", "Fidan",
]
LAST_NAMES = [
    "Mammadov", "Aliyev", "Hasanov", "Huseynov", "Guliyev", "Rzayev", "Bayramov",
    "Ismayilov", "Maharramov", "Abbasov", "Musayev", "Karimov", "Ibrahimov",
    "Hajiyev", "Namazov", "Sadigov", "Valiyev", "Orujov", "Jafarov", "Ahmadov",
    "Suleymanov", "Rahimov", "Taghiyev", "Gasimov", "Mikayilov",
]


def random_name():
    gender = random.choice(["M", "F"])
    fn = random.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
    ln = random.choice(LAST_NAMES)
    if gender == "F" and not ln.endswith("a"):
        ln = ln + "a"
    return fn, ln, gender


def random_date(start: date, end: date) -> str:
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def random_dob(min_age=18, max_age=25) -> str:
    today = date(2026, 4, 1)
    start = today - timedelta(days=max_age * 365)
    end = today - timedelta(days=min_age * 365)
    return random_date(start, end)


# ============================================================
# UNIVERSITY
# ============================================================

def generate_university():
    db_path = os.path.join(SCRIPT_DIR, "university", "source.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    schema_path = os.path.join(SCRIPT_DIR, "schemas", "university_schema.sql")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    with open(schema_path) as f:
        cur.executescript(f.read())

    # Programs
    programs = [
        ("Computer Science", "CS", "Faculty of IT", "bachelor", 4),
        ("Business Administration", "BA", "Faculty of Economics", "bachelor", 4),
        ("Civil Engineering", "CE", "Faculty of Engineering", "bachelor", 4),
        ("Medicine", "MED", "Faculty of Medicine", "bachelor", 6),
        ("Azerbaijani Language & Literature", "ALL", "Faculty of Humanities", "bachelor", 4),
    ]
    for name, code, dept, level, dur in programs:
        cur.execute(
            "INSERT INTO programs (name, code, department, level, duration_years) VALUES (?, ?, ?, ?, ?)",
            (name, code, dept, level, dur),
        )

    # Courses per program
    cs_courses = [
        ("Introduction to Programming", "CS101", 1), ("Data Structures", "CS201", 2),
        ("Algorithms", "CS301", 3), ("Database Systems", "CS202", 2),
        ("Web Development", "CS302", 3), ("Machine Learning", "CS401", 4),
        ("Software Engineering", "CS303", 3), ("Operating Systems", "CS304", 3),
    ]
    ba_courses = [
        ("Principles of Management", "BA101", 1), ("Microeconomics", "BA102", 1),
        ("Financial Accounting", "BA201", 2), ("Marketing", "BA202", 2),
        ("Business Statistics", "BA301", 3), ("Strategic Management", "BA401", 4),
    ]
    ce_courses = [
        ("Engineering Mathematics", "CE101", 1), ("Structural Analysis", "CE201", 2),
        ("Geotechnics", "CE301", 3), ("Construction Management", "CE302", 3),
        ("Concrete Structures", "CE401", 4), ("Hydraulics", "CE202", 2),
    ]
    med_courses = [
        ("Anatomy", "MED101", 1), ("Physiology", "MED102", 1),
        ("Biochemistry", "MED201", 2), ("Pathology", "MED301", 3),
        ("Pharmacology", "MED302", 3), ("Clinical Medicine", "MED401", 4),
    ]
    all_lit_courses = [
        ("Azerbaijani Grammar", "ALL101", 1), ("Classical Literature", "ALL102", 1),
        ("Modern Azerbaijani Literature", "ALL201", 2), ("Linguistics", "ALL301", 3),
        ("Literary Criticism", "ALL302", 3), ("Translation Studies", "ALL401", 4),
    ]

    program_courses = {1: cs_courses, 2: ba_courses, 3: ce_courses, 4: med_courses, 5: all_lit_courses}
    for prog_id, courses in program_courses.items():
        for name, code, sem in courses:
            cur.execute(
                "INSERT INTO courses (program_id, name, code, credits, semester) VALUES (?, ?, ?, ?, ?)",
                (prog_id, name, code, 3.0, sem),
            )

    # Students — enrollment size reflects trends
    # CS: growing (more recent students), Literature: declining
    program_student_counts = {1: 160, 2: 130, 3: 110, 4: 100, 5: 80}  # total ~580
    # Difficulty / base GPA ranges per program
    program_profiles = {
        1: {"base_gpa": 3.1, "gpa_std": 0.6, "attendance_base": 82, "dropout_pct": 0.10},
        2: {"base_gpa": 2.9, "gpa_std": 0.5, "attendance_base": 78, "dropout_pct": 0.12},
        3: {"base_gpa": 2.7, "gpa_std": 0.6, "attendance_base": 75, "dropout_pct": 0.14},
        4: {"base_gpa": 3.3, "gpa_std": 0.4, "attendance_base": 92, "dropout_pct": 0.05},
        5: {"base_gpa": 2.8, "gpa_std": 0.5, "attendance_base": 70, "dropout_pct": 0.16},
    }

    student_id = 0
    all_students = []  # (student_id, program_id, semester, attendance_pct, gpa, status)

    for prog_id, count in program_student_counts.items():
        profile = program_profiles[prog_id]
        for i in range(count):
            student_id += 1
            fn, ln, gender = random_name()
            code = f"BEU-{student_id:04d}"
            email = f"{fn.lower()}.{ln.lower()}@beu.edu.az"

            # Distribute semesters: more first-year for growing programs (CS), fewer for declining (Literature)
            if prog_id == 1:  # CS growing
                semester = random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[20, 18, 15, 13, 10, 9, 8, 7])[0]
            elif prog_id == 5:  # Literature declining
                semester = random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[8, 9, 10, 12, 14, 15, 16, 16])[0]
            else:
                semester = random.randint(1, 8)

            year = (semester - 1) // 2 + 1
            enroll_year = 2026 - year
            enrollment_date = f"{enroll_year}-09-{random.randint(1,15):02d}"
            dob = random_dob(17 + year, 20 + year)

            # Dropout logic: higher in first year
            is_dropped = False
            drop_pct = profile["dropout_pct"] * (2.5 if semester <= 2 else 0.5 if semester >= 6 else 1.0)
            if random.random() < drop_pct:
                is_dropped = True

            # Attendance — correlated with semester and randomness
            att_base = profile["attendance_base"]
            attendance_pct = max(30, min(100, att_base + random.gauss(0, 12)))
            if is_dropped:
                attendance_pct = max(30, attendance_pct - random.uniform(15, 30))

            # GPA — correlated with attendance
            att_factor = (attendance_pct - 50) / 50  # -0.4 to 1.0
            gpa = profile["base_gpa"] + att_factor * 0.8 + random.gauss(0, profile["gpa_std"] * 0.5)
            gpa = max(0.5, min(4.0, round(gpa, 2)))

            status = "dropped" if is_dropped else "active"
            if not is_dropped and gpa < 1.5:
                status = "probation"

            cur.execute(
                """INSERT INTO students (student_code, first_name, last_name, email,
                   date_of_birth, gender, enrollment_date, current_gpa, current_semester, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (code, fn, ln, email, dob, gender, enrollment_date, gpa, semester, status),
            )

            all_students.append((student_id, prog_id, semester, attendance_pct, gpa, status))

            # Enrollment record
            enroll_status = "dropped" if is_dropped else ("completed" if semester == 8 else "active")
            dropped_at = None
            if is_dropped:
                drop_month = random.randint(1, 6)
                dropped_at = f"{enroll_year + (semester // 2)}-{drop_month:02d}-{random.randint(1,28):02d}"

            cur.execute(
                """INSERT INTO enrollments (student_id, program_id, status, enrolled_at, dropped_at, drop_reason, final_gpa)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    student_id, prog_id, enroll_status, enrollment_date,
                    dropped_at,
                    random.choice(["Financial", "Personal", "Academic", "Transfer"]) if is_dropped else None,
                    gpa if enroll_status == "completed" else None,
                ),
            )

    # Attendance records — generate for the current semester (Jan-Apr 2026)
    cur.execute("SELECT id, program_id FROM courses")
    course_rows = cur.fetchall()
    course_by_program = {}
    for cid, pid in course_rows:
        course_by_program.setdefault(pid, []).append(cid)

    session_dates = []
    d = date(2026, 1, 13)
    while d <= date(2026, 4, 4):
        if d.weekday() < 5:  # weekdays
            session_dates.append(d.isoformat())
        d += timedelta(days=1)

    attendance_statuses = ["present", "absent", "late", "excused"]

    for sid, prog_id, semester, att_pct, gpa, status in all_students:
        if status == "dropped" and random.random() < 0.5:
            continue  # some dropped students have no recent data

        prog_courses = course_by_program.get(prog_id, [])
        # Each student takes 2-3 courses per semester
        student_courses = random.sample(prog_courses, min(3, len(prog_courses)))

        for cid in student_courses:
            # ~2 sessions per week per course, sample some dates
            n_sessions = random.randint(15, 25)
            dates = random.sample(session_dates, min(n_sessions, len(session_dates)))
            for sd in dates:
                if random.random() * 100 < att_pct:
                    att_status = random.choices(["present", "late"], weights=[90, 10])[0]
                else:
                    att_status = random.choices(["absent", "excused"], weights=[80, 20])[0]
                cur.execute(
                    "INSERT INTO attendance (student_id, course_id, session_date, status) VALUES (?, ?, ?, ?)",
                    (sid, cid, sd, att_status),
                )

    # Assessments
    assessment_types = ["midterm", "assignment", "quiz", "final"]
    for sid, prog_id, semester, att_pct, gpa, status in all_students:
        if status == "dropped" and random.random() < 0.3:
            continue

        prog_courses = course_by_program.get(prog_id, [])
        student_courses = random.sample(prog_courses, min(3, len(prog_courses)))

        for cid in student_courses:
            for atype in assessment_types:
                # Score correlated with GPA
                base_score = (gpa / 4.0) * 80 + random.gauss(0, 10)
                score = max(10, min(100, round(base_score, 1)))
                grade = (
                    "A" if score >= 85 else
                    "B" if score >= 70 else
                    "C" if score >= 55 else
                    "D" if score >= 40 else "F"
                )
                month = {"midterm": 2, "assignment": 3, "quiz": 1, "final": 4}[atype]
                assessed_at = f"2026-{month:02d}-{random.randint(5, 25):02d}"
                cur.execute(
                    """INSERT INTO assessments (student_id, course_id, type, title, score, max_score, grade, assessed_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sid, cid, atype, f"{atype.title()} Exam", score, 100, grade, assessed_at),
                )

    conn.commit()
    conn.close()
    print(f"University mock DB created: {db_path}")
    print(f"  Students: {len(all_students)}")


# ============================================================
# COURSE PROVIDER
# ============================================================

def generate_course_provider():
    db_path = os.path.join(SCRIPT_DIR, "course_provider", "source.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    schema_path = os.path.join(SCRIPT_DIR, "schemas", "provider_schema.sql")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    with open(schema_path) as f:
        cur.executescript(f.read())

    # Programs (short courses)
    programs = [
        ("Web Development Bootcamp", "WEB", "technology", 16),
        ("Data Science Fundamentals", "DS", "technology", 20),
        ("Digital Marketing", "DM", "business", 12),
        ("UI/UX Design", "UX", "design", 14),
        ("Cybersecurity Essentials", "CYB", "technology", 16),
        ("Cloud Computing", "CLD", "technology", 12),
        ("Project Management", "PM", "business", 10),
        ("AI & Machine Learning", "AIML", "technology", 20),
    ]
    for name, code, cat, weeks in programs:
        cur.execute(
            "INSERT INTO programs (name, code, category, duration_weeks) VALUES (?, ?, ?, ?)",
            (name, code, cat, weeks),
        )

    # Modules (courses) per program
    program_modules = {
        1: [("HTML & CSS", "WEB-1", 1), ("JavaScript", "WEB-2", 2), ("React", "WEB-3", 3), ("Backend & APIs", "WEB-4", 4)],
        2: [("Python Basics", "DS-1", 1), ("Statistics", "DS-2", 2), ("Data Viz", "DS-3", 3), ("ML Intro", "DS-4", 4), ("Capstone Project", "DS-5", 5)],
        3: [("Marketing Fundamentals", "DM-1", 1), ("Social Media", "DM-2", 2), ("SEO & SEM", "DM-3", 3), ("Analytics", "DM-4", 4)],
        4: [("Design Thinking", "UX-1", 1), ("Figma Workshop", "UX-2", 2), ("User Research", "UX-3", 3), ("Portfolio", "UX-4", 4)],
        5: [("Network Security", "CYB-1", 1), ("Cryptography", "CYB-2", 2), ("Ethical Hacking", "CYB-3", 3), ("Incident Response", "CYB-4", 4)],
        6: [("Cloud Basics", "CLD-1", 1), ("AWS/Azure", "CLD-2", 2), ("DevOps", "CLD-3", 3)],
        7: [("PM Fundamentals", "PM-1", 1), ("Agile & Scrum", "PM-2", 2), ("Tools & Practice", "PM-3", 3)],
        8: [("AI Foundations", "AIML-1", 1), ("Deep Learning", "AIML-2", 2), ("NLP", "AIML-3", 3), ("Computer Vision", "AIML-4", 4), ("Final Project", "AIML-5", 5)],
    }
    for prog_id, modules in program_modules.items():
        for name, code, mod_num in modules:
            cur.execute(
                "INSERT INTO courses (program_id, name, code, module_number) VALUES (?, ?, ?, ?)",
                (prog_id, name, code, mod_num),
            )

    # Students per program (reflects demand)
    program_student_counts = {1: 45, 2: 50, 3: 30, 4: 25, 5: 20, 6: 22, 7: 18, 8: 40}  # ~250
    program_profiles = {
        1: {"completion": 0.80, "attendance_base": 82, "score_base": 72},
        2: {"completion": 0.75, "attendance_base": 80, "score_base": 68},
        3: {"completion": 0.70, "attendance_base": 74, "score_base": 70},
        4: {"completion": 0.78, "attendance_base": 80, "score_base": 75},
        5: {"completion": 0.72, "attendance_base": 78, "score_base": 65},
        6: {"completion": 0.74, "attendance_base": 76, "score_base": 67},
        7: {"completion": 0.60, "attendance_base": 68, "score_base": 65},  # PM lower engagement
        8: {"completion": 0.70, "attendance_base": 79, "score_base": 66},
    }

    student_id = 0
    all_students = []

    for prog_id, count in program_student_counts.items():
        profile = program_profiles[prog_id]
        for i in range(count):
            student_id += 1
            fn, ln, gender = random_name()
            code = f"ADA-{student_id:04d}"
            email = f"{fn.lower()}.{ln.lower()}@learn.az"
            dob = random_dob(20, 35)

            # Enrollment dates spread over recent cohorts
            cohort = random.choices([1, 2, 3], weights=[50, 30, 20])[0]  # 1=current, 2=previous, 3=older
            enroll_month = {1: "2026-01", 2: "2025-09", 3: "2025-05"}[cohort]
            enrollment_date = f"{enroll_month}-{random.randint(1,15):02d}"

            # Dropout: higher in first month (20%)
            is_dropped = False
            if cohort == 1 and random.random() < 0.20:
                is_dropped = True
            elif cohort >= 2 and random.random() < (1 - profile["completion"]) * 0.6:
                is_dropped = True

            status = "dropped" if is_dropped else ("completed" if cohort == 3 else "active")

            cur.execute(
                """INSERT INTO students (student_code, first_name, last_name, email,
                   date_of_birth, gender, enrollment_date, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (code, fn, ln, email, dob, gender, enrollment_date, status),
            )

            att_pct = max(40, min(100, profile["attendance_base"] + random.gauss(0, 12)))
            if is_dropped:
                att_pct = max(30, att_pct - random.uniform(10, 25))

            all_students.append((student_id, prog_id, att_pct, status, cohort))

            enroll_status = status
            dropped_at = None
            if is_dropped:
                weeks_in = random.randint(1, 6)
                d = date.fromisoformat(enrollment_date) + timedelta(weeks=weeks_in)
                dropped_at = d.isoformat()

            cur.execute(
                """INSERT INTO enrollments (student_id, program_id, status, enrolled_at, dropped_at, drop_reason)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    student_id, prog_id, enroll_status, enrollment_date,
                    dropped_at,
                    random.choice(["Time constraints", "Financial", "Found job", "Not relevant"]) if is_dropped else None,
                ),
            )

    # Attendance
    cur.execute("SELECT id, program_id FROM courses")
    course_rows = cur.fetchall()
    course_by_program = {}
    for cid, pid in course_rows:
        course_by_program.setdefault(pid, []).append(cid)

    session_dates = []
    d = date(2026, 1, 13)
    while d <= date(2026, 4, 4):
        if d.weekday() < 6:
            session_dates.append(d.isoformat())
        d += timedelta(days=1)

    for sid, prog_id, att_pct, status, cohort in all_students:
        if status == "dropped" and cohort >= 2:
            continue
        prog_courses = course_by_program.get(prog_id, [])
        for cid in prog_courses:
            n_sessions = random.randint(10, 18)
            dates = random.sample(session_dates, min(n_sessions, len(session_dates)))
            for sd in dates:
                if random.random() * 100 < att_pct:
                    att_status = random.choices(["present", "late"], weights=[85, 15])[0]
                else:
                    att_status = random.choices(["absent", "excused"], weights=[85, 15])[0]
                cur.execute(
                    "INSERT INTO attendance (student_id, course_id, session_date, status) VALUES (?, ?, ?, ?)",
                    (sid, cid, sd, att_status),
                )

    # Assessments
    for sid, prog_id, att_pct, status, cohort in all_students:
        if status == "dropped" and random.random() < 0.4:
            continue
        profile = program_profiles[prog_id]
        prog_courses = course_by_program.get(prog_id, [])
        for cid in prog_courses:
            for atype in ["quiz", "assignment", "project"]:
                att_factor = (att_pct - 50) / 50
                base = profile["score_base"] + att_factor * 15 + random.gauss(0, 8)
                score = max(15, min(100, round(base, 1)))
                grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"
                month = {"quiz": 2, "assignment": 3, "project": 4}[atype]
                assessed_at = f"2026-{month:02d}-{random.randint(5, 25):02d}"
                cur.execute(
                    """INSERT INTO assessments (student_id, course_id, type, title, score, max_score, grade, assessed_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sid, cid, atype, f"{atype.title()}", score, 100, grade, assessed_at),
                )

    conn.commit()
    conn.close()
    print(f"Course provider mock DB created: {db_path}")
    print(f"  Students: {len(all_students)}")


if __name__ == "__main__":
    generate_university()
    generate_course_provider()
    print("\nDone! Mock databases generated successfully.")
