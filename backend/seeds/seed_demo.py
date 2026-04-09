"""
Seed script: creates demo institutions, users, sync jobs, runs full sync,
computes analytics, and seeds labour market data + recommendations.

Usage: python -m seeds.seed_demo
"""

import json
import os
import sys
import uuid
from datetime import date, datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.database import sync_engine, SyncSessionLocal, Base
from app.models import *  # noqa — registers all models
from app.api.deps import hash_password
from app.sync.engine import run_sync, SYNC_ORDER
from app.sync.loaders.postgres_loader import clear_caches
from app.analytics.aggregator import compute_student_scores, compute_program_scores, compute_institution_kpis

settings = get_settings()
MOCK_PATH = os.environ.get("MOCK_SOURCES_PATH", settings.MOCK_SOURCES_PATH)


def seed():
    # Create all tables
    Base.metadata.create_all(sync_engine)

    db = SyncSessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Institution).first()
        if existing:
            print("Database already seeded. Skipping.")
            print("  To re-seed, drop and recreate the database.")
            return

        # Seed institution types and roles (if migration didn't run)
        if not db.query(InstitutionType).first():
            for name, display in [("university", "University"), ("course_provider", "Course Provider"),
                                   ("academy", "Academy"), ("training_center", "Training Center")]:
                db.add(InstitutionType(name=name, display_name=display))
            db.commit()

        if not db.query(Role).first():
            for name, desc in [("admin", "Full access"), ("analyst", "Analytics access"), ("viewer", "Read-only")]:
                db.add(Role(name=name, description=desc))
            db.commit()

        uni_type = db.query(InstitutionType).filter(InstitutionType.name == "university").first()
        provider_type = db.query(InstitutionType).filter(InstitutionType.name == "course_provider").first()
        admin_role = db.query(Role).filter(Role.name == "admin").first()

        # ---- Institution 1: University ----
        uni = Institution(
            name="Baku Engineering University",
            type_id=uni_type.id,
            slug="beu",
            city="Baku",
            contact_email="admin@beu.edu.az",
            website="https://beu.edu.az",
        )
        db.add(uni)
        db.flush()

        uni_admin = User(
            institution_id=uni.id,
            role_id=admin_role.id,
            email="admin@beu.edu.az",
            password_hash=hash_password("demo123"),
            full_name="BEU Admin",
        )
        db.add(uni_admin)

        uni_db_path = os.path.abspath(os.path.join(MOCK_PATH, "university", "source.db"))
        uni_sync = SyncJob(
            institution_id=uni.id,
            name="BEU Student Information System",
            source_type="sqlite",
            connection_config_json=json.dumps({"db_path": uni_db_path}),
            tables_to_sync_json=json.dumps(SYNC_ORDER),
            schedule_cron="*/15 * * * *",
        )
        db.add(uni_sync)

        # ---- Institution 2: Course Provider ----
        academy = Institution(
            name="Azerbaijan Digital Academy",
            type_id=provider_type.id,
            slug="ada-academy",
            city="Baku",
            contact_email="admin@digitalacademy.az",
            website="https://digitalacademy.az",
        )
        db.add(academy)
        db.flush()

        academy_admin = User(
            institution_id=academy.id,
            role_id=admin_role.id,
            email="admin@digitalacademy.az",
            password_hash=hash_password("demo123"),
            full_name="ADA Admin",
        )
        db.add(academy_admin)

        academy_db_path = os.path.abspath(os.path.join(MOCK_PATH, "course_provider", "source.db"))
        academy_sync = SyncJob(
            institution_id=academy.id,
            name="ADA Learning Management System",
            source_type="sqlite",
            connection_config_json=json.dumps({"db_path": academy_db_path}),
            tables_to_sync_json=json.dumps(SYNC_ORDER),
            schedule_cron="*/15 * * * *",
        )
        db.add(academy_sync)

        db.commit()
        print("Institutions and users created.")
        print(f"  University login: admin@beu.edu.az / demo123")
        print(f"  Course provider login: admin@digitalacademy.az / demo123")

        # ---- Run full sync for both (requires mock source DBs) ----
        sync_ok = False
        try:
            print("\nRunning full sync for University...")
            clear_caches()
            run_sync(db, str(uni_sync.id), "full")

            print("Running full sync for Course Provider...")
            clear_caches()
            run_sync(db, str(academy_sync.id), "full")
            sync_ok = True
        except Exception as e:
            print(f"\n  WARNING: Sync failed ({e})")
            print("  This is expected if mock source DBs are not available.")
            print("  Login will still work. Dashboard will show empty data.")

        # ---- Compute analytics (requires synced data) ----
        if sync_ok:
            try:
                print("\nComputing analytics for University...")
                compute_student_scores(db, str(uni.id))
                compute_program_scores(db, str(uni.id))
                compute_institution_kpis(db, str(uni.id))

                print("Computing analytics for Course Provider...")
                compute_student_scores(db, str(academy.id))
                compute_program_scores(db, str(academy.id))
                compute_institution_kpis(db, str(academy.id))
            except Exception as e:
                print(f"\n  WARNING: Analytics computation failed ({e})")
        else:
            print("\nSkipping analytics (no synced data).")

        # ---- Seed labour market data ----
        print("\nSeeding labour market & skills data...")
        seed_labour_market(db)

        # ---- Seed recommendations ----
        print("Generating recommendations...")
        seed_recommendations(db, uni.id, academy.id)

        print("\nSeed complete!")

    finally:
        db.close()


def seed_labour_market(db):
    trends = [
        ("Software Developer", "Technology", "high", 22.0, 2500, 450),
        ("Data Analyst", "Technology", "high", 30.0, 2200, 380),
        ("Cybersecurity Specialist", "Technology", "high", 25.0, 2800, 220),
        ("Cloud Engineer", "Technology", "high", 28.0, 3000, 180),
        ("AI/ML Engineer", "Technology", "high", 35.0, 3500, 150),
        ("Digital Marketing Specialist", "Business", "medium", 5.0, 1500, 300),
        ("Civil Engineer", "Engineering", "medium", 8.0, 2000, 250),
        ("Project Manager", "Business", "medium", 6.0, 2200, 200),
        ("Medical Doctor", "Healthcare", "high", 12.0, 3000, 180),
        ("UI/UX Designer", "Design", "high", 15.0, 2000, 160),
        ("Accountant", "Business", "low", -2.0, 1200, 350),
        ("Administrative Assistant", "General", "declining", -10.0, 800, 200),
        ("Language Teacher", "Education", "low", -5.0, 1000, 120),
        ("Web Developer", "Technology", "high", 18.0, 2200, 400),
        ("DevOps Engineer", "Technology", "high", 28.0, 2800, 170),
    ]
    for occ, sector, demand, growth, salary, postings in trends:
        db.add(LabourMarketTrend(
            occupation=occ, sector=sector, demand_level=demand,
            growth_rate=growth, avg_salary_azn=salary, job_postings=postings,
            data_source="Azerbaijan State Statistics + LinkedIn (simulated)",
            observed_at=date(2026, 4, 1),
        ))

    skills = [
        ("Python", "technical", "high", 30.0, "growing"),
        ("SQL", "technical", "high", 15.0, "stable"),
        ("JavaScript", "technical", "high", 12.0, "stable"),
        ("React", "technical", "high", 18.0, "growing"),
        ("Machine Learning", "technical", "emerging", 35.0, "growing"),
        ("Cloud Platforms (AWS/Azure)", "technical", "high", 28.0, "growing"),
        ("Data Visualization", "technical", "high", 20.0, "growing"),
        ("Cybersecurity", "technical", "high", 25.0, "growing"),
        ("Project Management", "soft", "medium", 6.0, "stable"),
        ("Communication", "soft", "medium", 3.0, "stable"),
        ("UX Research", "technical", "emerging", 15.0, "growing"),
        ("API Design", "technical", "emerging", 20.0, "growing"),
        ("Manual Data Entry", "technical", "declining", -15.0, "declining"),
        ("Basic Office Suite", "technical", "declining", -10.0, "declining"),
        ("DevOps/CI-CD", "technical", "high", 28.0, "growing"),
        ("NLP", "technical", "emerging", 32.0, "growing"),
    ]
    for name, cat, demand, growth, outlook in skills:
        db.add(SkillTrend(
            skill_name=name, category=cat, demand_level=demand,
            growth_rate=growth, future_outlook=outlook,
            data_source="World Economic Forum + LinkedIn (simulated)",
            observed_at=date(2026, 4, 1),
        ))

    db.commit()


def seed_recommendations(db, uni_id, academy_id):
    recs = [
        # University recommendations
        (uni_id, "institution", None, "new_program", "Launch Data Science Specialization",
         "Market demand for data science skills is growing 30% YoY. Your Computer Science program already covers 60% of prerequisite skills. Adding a Data Science track would attract high-demand students and improve employment outcomes.",
         True, 92),
        (uni_id, "program", None, "curriculum", "Update Language & Literature Program",
         "Enrollment is declining 10% YoY and labour market demand for traditional language skills is low. Consider adding digital content creation, translation technology, and computational linguistics modules.",
         True, 78),
        (uni_id, "institution", None, "intervention", "Implement First-Year Early Warning System",
         "15% of first-year students are dropping out. Targeted mentoring for students with attendance below 75% in the first 4 weeks could reduce first-year dropout by 30-40%.",
         True, 85),
        (uni_id, "program", None, "resource", "Increase Engineering Lab Capacity",
         "Civil Engineering has the lowest average scores. Student feedback indicates insufficient lab time. Expanding lab hours could improve practical skill development.",
         False, 65),
        (uni_id, "institution", None, "policy", "Attendance-Linked Academic Support",
         "Strong correlation detected: students with attendance below 70% have GPAs 1.5 points lower on average. Automatic referral to academic support when attendance drops below 75% is recommended.",
         True, 80),

        # Course provider recommendations
        (academy_id, "institution", None, "new_program", "Add Cybersecurity Advanced Track",
         "Cybersecurity demand is surging (+25% growth) but your current Essentials course is introductory. An advanced track covering penetration testing and incident response would fill a critical market gap.",
         True, 88),
        (academy_id, "program", None, "curriculum", "Refresh Project Management Curriculum",
         "PM program has the lowest completion rate (60%) and below-average engagement. Consider adding Agile certifications prep and real-world case studies from local companies.",
         True, 72),
        (academy_id, "institution", None, "intervention", "First-Month Onboarding Enhancement",
         "20% of students drop out in the first month. A structured onboarding week with mentoring, clear milestone expectations, and early success experiences could significantly reduce early dropout.",
         True, 90),
        (academy_id, "program", None, "new_program", "Launch Cloud & DevOps Bootcamp",
         "Cloud/DevOps skills are growing 28% YoY with very few local training options. Your Cloud Computing course covers basics — a full DevOps bootcamp would meet unserved demand.",
         True, 85),
    ]
    for inst_id, level, target, category, title, desc, ai, priority in recs:
        db.add(Recommendation(
            institution_id=inst_id, level=level, target_id=target,
            category=category, title=title, description=desc,
            ai_generated=ai, priority_score=priority,
        ))
    db.commit()


if __name__ == "__main__":
    seed()
