"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-08
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Institution types
    op.create_table(
        "institution_types",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Institutions
    op.create_table(
        "institutions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type_id", sa.Integer, sa.ForeignKey("institution_types.id"), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("address", sa.Text),
        sa.Column("city", sa.String(100)),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("contact_phone", sa.String(50)),
        sa.Column("logo_url", sa.Text),
        sa.Column("website", sa.String(255)),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.String(255)),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Programs
    op.create_table(
        "programs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50)),
        sa.Column("level", sa.String(50)),
        sa.Column("department", sa.String(255)),
        sa.Column("duration_months", sa.Integer),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", "source_id", name="uq_programs_inst_source"),
    )

    # Courses
    op.create_table(
        "courses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("program_id", sa.String(36), sa.ForeignKey("programs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50)),
        sa.Column("credits", sa.Numeric(4, 1)),
        sa.Column("semester", sa.Integer),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", "source_id", name="uq_courses_inst_source"),
    )

    # Students
    op.create_table(
        "students",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("student_code", sa.String(50)),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("date_of_birth", sa.Date),
        sa.Column("gender", sa.String(20)),
        sa.Column("enrollment_date", sa.Date),
        sa.Column("current_gpa", sa.Numeric(4, 2)),
        sa.Column("current_semester", sa.Integer),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", "source_id", name="uq_students_inst_source"),
    )

    # Enrollments
    op.create_table(
        "enrollments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("program_id", sa.String(36), sa.ForeignKey("programs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("enrolled_at", sa.Date, nullable=False),
        sa.Column("completed_at", sa.Date),
        sa.Column("dropped_at", sa.Date),
        sa.Column("drop_reason", sa.Text),
        sa.Column("final_gpa", sa.Numeric(4, 2)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", "source_id", name="uq_enrollments_inst_source"),
    )

    # Attendance
    op.create_table(
        "attendance_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("session_date", sa.Date, nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Assessments
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("score", sa.Numeric(6, 2)),
        sa.Column("max_score", sa.Numeric(6, 2), nullable=False, server_default="100"),
        sa.Column("percentage", sa.Numeric(5, 2)),
        sa.Column("grade", sa.String(5)),
        sa.Column("assessed_at", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Student statuses
    op.create_table(
        "student_statuses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("reason", sa.String(500)),
        sa.Column("effective_date", sa.Date, nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("level", sa.String(30), nullable=False),
        sa.Column("target_id", sa.String(36)),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("ai_generated", sa.Boolean, server_default=sa.text("false")),
        sa.Column("priority_score", sa.Numeric(5, 2)),
        sa.Column("status", sa.String(30), server_default="active"),
        sa.Column("data_snapshot", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Labour market trends
    op.create_table(
        "labour_market_trends",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("occupation", sa.String(255), nullable=False),
        sa.Column("sector", sa.String(100)),
        sa.Column("region", sa.String(100), server_default="Azerbaijan"),
        sa.Column("demand_level", sa.String(20)),
        sa.Column("growth_rate", sa.Numeric(6, 2)),
        sa.Column("avg_salary_azn", sa.Numeric(10, 2)),
        sa.Column("job_postings", sa.Integer),
        sa.Column("data_source", sa.String(255)),
        sa.Column("observed_at", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Skill trends
    op.create_table(
        "skill_trends",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("skill_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("demand_level", sa.String(20)),
        sa.Column("growth_rate", sa.Numeric(6, 2)),
        sa.Column("relevance_to", sa.Text),
        sa.Column("future_outlook", sa.String(20)),
        sa.Column("data_source", sa.String(255)),
        sa.Column("observed_at", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Analytics: student scores
    op.create_table(
        "analytics_student_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("dropout_risk", sa.Numeric(5, 2)),
        sa.Column("performance_risk", sa.Numeric(5, 2)),
        sa.Column("attendance_rate", sa.Numeric(5, 2)),
        sa.Column("avg_score", sa.Numeric(5, 2)),
        sa.Column("gpa_trend", sa.String(20)),
        sa.Column("risk_factors", sa.Text),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Analytics: program scores
    op.create_table(
        "analytics_program_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("program_id", sa.String(36), sa.ForeignKey("programs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("performance_score", sa.Numeric(5, 2)),
        sa.Column("completion_rate", sa.Numeric(5, 2)),
        sa.Column("pass_rate", sa.Numeric(5, 2)),
        sa.Column("avg_gpa", sa.Numeric(4, 2)),
        sa.Column("dropout_rate", sa.Numeric(5, 2)),
        sa.Column("enrollment_trend", sa.String(20)),
        sa.Column("relevance_score", sa.Numeric(5, 2)),
        sa.Column("demand_trend", sa.String(20)),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Analytics: institution KPIs
    op.create_table(
        "analytics_institution_kpis",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period", sa.String(20), nullable=False),
        sa.Column("total_students", sa.Integer),
        sa.Column("active_students", sa.Integer),
        sa.Column("total_programs", sa.Integer),
        sa.Column("avg_gpa", sa.Numeric(4, 2)),
        sa.Column("overall_attendance", sa.Numeric(5, 2)),
        sa.Column("overall_pass_rate", sa.Numeric(5, 2)),
        sa.Column("overall_dropout_rate", sa.Numeric(5, 2)),
        sa.Column("at_risk_students", sa.Integer),
        sa.Column("high_risk_students", sa.Integer),
        sa.Column("avg_program_score", sa.Numeric(5, 2)),
        sa.Column("avg_relevance_score", sa.Numeric(5, 2)),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", "period", name="uq_kpi_inst_period"),
    )

    # Sync jobs
    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("connection_config_json", sa.Text, nullable=False),
        sa.Column("tables_to_sync_json", sa.Text, nullable=False),
        sa.Column("schedule_cron", sa.String(50)),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Sync job runs
    op.create_table(
        "sync_job_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sync_job_id", sa.String(36), sa.ForeignKey("sync_jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("sync_type", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("records_synced", sa.Integer, server_default="0"),
        sa.Column("records_failed", sa.Integer, server_default="0"),
        sa.Column("error_summary", sa.Text),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Sync checkpoints
    op.create_table(
        "sync_checkpoints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sync_job_id", sa.String(36), sa.ForeignKey("sync_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("table_name", sa.String(100), nullable=False),
        sa.Column("last_synced_at", sa.DateTime, nullable=False),
        sa.Column("last_record_id", sa.String(100)),
        sa.Column("row_count", sa.Integer),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("sync_job_id", "table_name", name="uq_checkpoint_job_table"),
    )

    # Field mappings
    op.create_table(
        "field_mappings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_table", sa.String(100), nullable=False),
        sa.Column("source_field", sa.String(100), nullable=False),
        sa.Column("target_table", sa.String(100), nullable=False),
        sa.Column("target_field", sa.String(100), nullable=False),
        sa.Column("transform", sa.String(50)),
        sa.Column("transform_config", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Integration errors
    op.create_table(
        "integration_errors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sync_job_run_id", sa.String(36), sa.ForeignKey("sync_job_runs.id", ondelete="SET NULL")),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("error_type", sa.String(50), nullable=False),
        sa.Column("source_table", sa.String(100)),
        sa.Column("source_record_id", sa.String(100)),
        sa.Column("error_message", sa.Text, nullable=False),
        sa.Column("error_details", sa.Text),
        sa.Column("resolved", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Audit log
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("institution_id", sa.String(36), sa.ForeignKey("institutions.id"), index=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", sa.String(36)),
        sa.Column("details", sa.Text),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Seed reference data
    op.execute("""
        INSERT INTO institution_types (name, display_name) VALUES
            ('university', 'University'),
            ('course_provider', 'Course Provider'),
            ('academy', 'Academy'),
            ('training_center', 'Training Center');
    """)
    op.execute("""
        INSERT INTO roles (name, description) VALUES
            ('admin', 'Full access to institution settings, users, and all data'),
            ('analyst', 'Read access to all analytics, limited settings access'),
            ('viewer', 'Read-only access to dashboards and reports');
    """)


def downgrade() -> None:
    tables = [
        "audit_logs", "integration_errors", "field_mappings",
        "sync_checkpoints", "sync_job_runs", "sync_jobs",
        "analytics_institution_kpis", "analytics_program_scores", "analytics_student_scores",
        "skill_trends", "labour_market_trends", "recommendations",
        "student_statuses", "assessments", "attendance_records",
        "enrollments", "students", "courses", "programs",
        "users", "roles", "institutions", "institution_types",
    ]
    for t in tables:
        op.drop_table(t)
