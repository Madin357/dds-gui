# EduScope — Higher Education Intelligence Platform — MVP Plan

---

## 1. Product Definition

### Product Summary
A web-based analytics platform for universities and course providers in Azerbaijan. Institutions connect their student information systems; the platform automatically synchronizes data, computes risk scores and performance metrics, aligns programs with labour-market demand, and delivers actionable recommendations — all through a near-real-time dashboard.

### Target Users
| User Type | Examples |
|---|---|
| University administrators | Deans, department heads, academic affairs |
| Course provider managers | Academy directors, program coordinators |
| Institutional analysts | Data/reporting staff within institutions |

### Main Pain Points Solved
1. **No unified analytics** — institutions track data in fragmented systems with no consolidated view.
2. **Late intervention** — dropout and low-performance risks are detected too late.
3. **Curriculum-market disconnect** — programs are updated reactively, not proactively aligned to labour demand.
4. **Manual reporting** — KPIs are compiled manually in spreadsheets, often weeks late.
5. **No forecasting** — decisions about programs and enrollment are based on intuition, not data.

### MVP Feature Scope
| Module | MVP Scope |
|---|---|
| Dashboard | Institution KPIs, enrollment, attendance, pass/fail, dropout risk summary, program performance overview, top recommendations |
| Student Risk & Performance | Risk list, individual risk detail, attendance-performance chart, cohort comparison |
| Program / Course Analytics | Program comparison table, completion & pass rates, demand trend, strong vs weak breakdown |
| Skills & Labour Market | Current in-demand skills, future skills projection, declining professions, program alignment scores |
| Recommendations | AI-assisted institution-level and program-level suggestions with priority ranking |
| Forecasting | Enrollment and dropout predictions, program demand projections |
| Settings & Integrations | Institution profile, sync status, data source config, user roles, sync logs |
| Landing Page | Value proposition, sign-up / request demo, login |
| Auth | JWT login, role-based access (admin, analyst, viewer) |
| Sync Engine | Full initial sync, scheduled incremental sync, retry logic, error logging |

---

## 2. System Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                        │
│   Landing Page  │  Auth  │  Dashboard  │  Analytics  │  Settings    │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS / REST
┌────────────────────────────┴────────────────────────────────────────┐
│                        BACKEND (FastAPI)                            │
│   Auth  │  API Routes  │  Analytics Service  │  AI Service          │
└───┬──────────┬──────────────┬───────────────────────┬───────────────┘
    │          │              │                       │
    │    ┌─────┴─────┐  ┌────┴────┐           ┌──────┴──────┐
    │    │  Celery    │  │ Redis   │           │ Claude API  │
    │    │  Workers   │  │ Cache   │           │ (AI/LLM)    │
    │    └─────┬─────┘  └─────────┘           └─────────────┘
    │          │
    │    ┌─────┴──────────────────────────────────────┐
    │    │            SYNC ENGINE                      │
    │    │  Scheduler │ Extractor │ Transformer │ Load │
    │    └─────┬──────────────────────────────────────┘
    │          │
┌───┴──────────┴──────────────────────────────────────────────────────┐
│                    PostgreSQL (Central Platform DB)                  │
│   Core Tables  │  Staging Tables  │  Analytics Tables  │  Sync Meta │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                        ▲
         │ Sync (read-only)                       │ Ingest (scheduled)
┌────────┴────────────┐              ┌────────────┴────────────┐
│ Institution Source   │              │ External Data Sources   │
│ Systems (mock DBs)   │              │ (Labour market, skills) │
└─────────────────────┘              └─────────────────────────┘
```

### Component Breakdown

**Frontend — Next.js 14 (App Router)**
- TypeScript, Tailwind CSS, Tremor (dashboard component library)
- Recharts for custom visualizations
- React Query (TanStack Query) for server-state management
- Next.js middleware for auth token verification
- Reason: App Router gives layouts/loading states for free; Tremor provides production-ready dashboard components; Tailwind keeps styling fast for a hackathon.

**Backend — FastAPI (Python 3.11+)**
- SQLAlchemy 2.0 ORM with async support
- Pydantic v2 for request/response validation
- Alembic for database migrations
- Reason: Python is the best ecosystem for data analytics, pandas integration, and LLM APIs. FastAPI auto-generates OpenAPI docs and is extremely fast to develop with.

**Task Queue — Celery + Redis**
- Celery Beat for scheduled sync tasks
- Celery workers for sync execution, analytics computation, AI calls
- Redis as both message broker and cache layer
- Reason: battle-tested async job system; Redis doubles as cache.

**Database — PostgreSQL 16**
- Core normalized tables (institutions, students, programs, etc.)
- Staging tables (raw synced data before transformation)
- Analytics tables (precomputed aggregations, scores)
- Sync metadata tables (jobs, runs, checkpoints, errors)
- Reason: best relational DB for analytics queries, JSON support for flexible field mappings, mature ecosystem.

**Analytics Layer**
- Deterministic scoring algorithms in Python (no AI for core metrics)
- Precomputed and cached in analytics tables
- Refreshed by Celery periodic tasks (every 15-30 min)
- Pandas for aggregation logic

**Recommendation Layer**
- Rule-based recommendations generated from analytics scores
- Claude API for natural-language explanation and curriculum suggestions
- All AI outputs labeled as AI-generated; humans make final decisions

**External Data Ingestion**
- Scheduled Celery tasks to fetch/update labour market and skills data
- Sources: mock data files for MVP (JSON/CSV), designed for future API integration
- Daily or weekly refresh cadence

**Security Model**
- JWT access tokens (short-lived) + refresh tokens
- bcrypt password hashing
- Role-based access: admin, analyst, viewer
- Read-only sync connections to source systems
- All API endpoints require authentication (except public landing)
- Audit logging for sensitive operations
- Pseudonymized student views available for non-admin roles
- CORS restricted to frontend origin

---

## 3. Build Order / Development Sequence

### Phase 1 — Foundation (Days 1-2)
1. Project scaffolding: monorepo with `frontend/`, `backend/`, `mock-sources/`
2. PostgreSQL schema design + Alembic initial migration
3. SQLAlchemy models for all core tables
4. Mock source databases: create SQLite DBs simulating a university and a course provider
5. Seed mock sources with realistic demo data

### Phase 2 — Sync Engine (Days 3-4)
6. Celery + Redis setup with Docker Compose
7. Sync engine: full initial sync (extract from mock source → stage → transform → load)
8. Incremental sync using `updated_at` checkpoints
9. Celery Beat schedule configuration
10. Sync job logging, error handling, retry logic

### Phase 3 — Backend APIs (Days 5-6)
11. Auth endpoints: register, login, refresh token, me
12. Institution CRUD endpoints
13. Student list/detail endpoints with filters
14. Program/course list endpoints
15. Sync management endpoints (trigger sync, view logs)

### Phase 4 — Analytics Engine (Days 7-8)
16. Dropout risk scoring algorithm
17. Low-performance risk scoring
18. Program performance scoring
19. Course relevance and labour-market alignment scoring
20. Analytics aggregation Celery tasks
21. Analytics API endpoints (KPIs, risk lists, program scores)

### Phase 5 — Dashboard UI (Days 9-10)
22. Next.js project setup with Tailwind + Tremor
23. Auth pages (login, register)
24. Layout: sidebar navigation, institution selector, header
25. Overview dashboard: KPI cards, enrollment chart, risk summary, top programs
26. Student risk page: risk table, individual detail, attendance-performance chart

### Phase 6 — Full Analytics UI (Days 11-12)
27. Program analytics page: comparison table, completion rates, demand trends
28. Skills & labour market page: demand charts, alignment scores, declining professions
29. Recommendations page: prioritized suggestion cards with AI explanations
30. Forecasting page: enrollment/dropout prediction charts
31. Settings page: institution profile, sync status, user roles, sync logs

### Phase 7 — Landing & Polish (Days 13-14)
32. Public landing page: hero, features, sign-up form
33. AI integration: recommendation explanations, analytics summaries
34. End-to-end testing with demo data
35. UI polish, loading states, error states
36. Demo script preparation

---

## 4. Database Design

### Entity Relationship Overview

```
institution_types 1──N institutions 1──N users
                                    1──N programs 1──N courses
                                    1──N students
                                    1──N sync_jobs 1──N sync_job_runs
                                                   1──N sync_checkpoints
                                                   1──N integration_errors

students N──N enrollments N──1 programs
students 1──N attendance_records N──1 courses
students 1──N assessments N──1 courses
students 1──N student_statuses

institutions 1──N recommendations
institutions 1──N field_mappings

labour_market_trends (global/regional reference data)
skill_trends (global/regional reference data)
```

### Table Purposes

| Table | Purpose |
|---|---|
| `institution_types` | Enum-like: university, course_provider, academy, training_center |
| `institutions` | Registered organizations using the platform |
| `users` | Platform login accounts (staff within institutions) |
| `roles` | Permission levels: admin, analyst, viewer |
| `students` | Student records synced from institution sources |
| `programs` | Degree programs (university) or course tracks (provider) |
| `courses` | Individual courses/modules within programs |
| `enrollments` | Student-to-program enrollment records with status |
| `attendance_records` | Per-session attendance entries |
| `assessments` | Exam/assignment scores per student per course |
| `student_statuses` | Time-series status tracking (active, warning, probation, dropped) |
| `recommendations` | Generated suggestions at institution/program/student level |
| `labour_market_trends` | External data: occupation demand, growth rates |
| `skill_trends` | External data: skill demand, future projections |
| `sync_jobs` | Configured sync job definitions per institution |
| `sync_job_runs` | Individual execution records for each sync run |
| `sync_checkpoints` | Last-synced timestamps per table per institution |
| `field_mappings` | Maps source system fields to platform schema |
| `integration_errors` | Logged errors during sync with context for debugging |

---

## 5. SQL Schema

```sql
-- ============================================================
-- EduScope — Higher Education Intelligence Platform
-- Database Schema for MVP
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- INSTITUTION & AUTH
-- ============================================================

CREATE TABLE institution_types (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL UNIQUE,  -- 'university', 'course_provider', 'academy', 'training_center'
    display_name    VARCHAR(100) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE institutions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    type_id         INT NOT NULL REFERENCES institution_types(id),
    slug            VARCHAR(100) NOT NULL UNIQUE,
    address         TEXT,
    city            VARCHAR(100),
    contact_email   VARCHAR(255),
    contact_phone   VARCHAR(50),
    logo_url        TEXT,
    website         VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE roles (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL UNIQUE,  -- 'admin', 'analyst', 'viewer'
    description     TEXT
);

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    role_id         INT NOT NULL REFERENCES roles(id),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- ACADEMIC DATA
-- ============================================================

CREATE TABLE programs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_id       VARCHAR(100),              -- ID in the source system
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50),
    level           VARCHAR(50),               -- 'bachelor', 'master', 'certificate', 'diploma', 'short_course'
    department      VARCHAR(255),
    duration_months INT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(institution_id, source_id)
);

CREATE TABLE courses (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id      UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_id       VARCHAR(100),
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50),
    credits         DECIMAL(4,1),
    semester        INT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(institution_id, source_id)
);

CREATE TABLE students (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_id       VARCHAR(100),              -- ID in the source system
    student_code    VARCHAR(50),               -- Student number/code
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(255),
    date_of_birth   DATE,
    gender          VARCHAR(20),
    enrollment_date DATE,
    current_gpa     DECIMAL(4,2),
    current_semester INT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(institution_id, source_id)
);

CREATE TABLE enrollments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    program_id      UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_id       VARCHAR(100),
    status          VARCHAR(30) NOT NULL DEFAULT 'active',  -- 'active', 'completed', 'dropped', 'suspended', 'transferred'
    enrolled_at     DATE NOT NULL,
    completed_at    DATE,
    dropped_at      DATE,
    drop_reason     TEXT,
    final_gpa       DECIMAL(4,2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(institution_id, source_id)
);

CREATE TABLE attendance_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id       UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_id       VARCHAR(100),
    session_date    DATE NOT NULL,
    status          VARCHAR(20) NOT NULL,       -- 'present', 'absent', 'late', 'excused'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_attendance_course ON attendance_records(course_id);
CREATE INDEX idx_attendance_date ON attendance_records(session_date);

CREATE TABLE assessments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id       UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_id       VARCHAR(100),
    type            VARCHAR(50) NOT NULL,       -- 'exam', 'midterm', 'assignment', 'quiz', 'project', 'final'
    title           VARCHAR(255),
    score           DECIMAL(6,2),
    max_score       DECIMAL(6,2) NOT NULL DEFAULT 100,
    percentage      DECIMAL(5,2),               -- computed: score/max_score * 100
    grade           VARCHAR(5),                 -- 'A', 'B', 'C', 'D', 'F' or numeric
    assessed_at     DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assessments_student ON assessments(student_id);
CREATE INDEX idx_assessments_course ON assessments(course_id);

CREATE TABLE student_statuses (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    status          VARCHAR(30) NOT NULL,       -- 'active', 'at_risk', 'probation', 'warning', 'dropped', 'graduated'
    reason          TEXT,
    effective_date  DATE NOT NULL,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_student_statuses_student ON student_statuses(student_id);

-- ============================================================
-- ANALYTICS & RECOMMENDATIONS
-- ============================================================

CREATE TABLE recommendations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    level           VARCHAR(30) NOT NULL,       -- 'institution', 'program', 'student'
    target_id       UUID,                       -- references program or student depending on level
    category        VARCHAR(50) NOT NULL,       -- 'curriculum', 'intervention', 'resource', 'policy', 'new_program'
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    ai_generated    BOOLEAN NOT NULL DEFAULT FALSE,
    priority_score  DECIMAL(5,2),               -- 0-100
    status          VARCHAR(30) NOT NULL DEFAULT 'active',  -- 'active', 'accepted', 'dismissed', 'implemented'
    data_snapshot   JSONB,                      -- supporting data at time of generation
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recommendations_institution ON recommendations(institution_id);

CREATE TABLE labour_market_trends (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    occupation      VARCHAR(255) NOT NULL,
    sector          VARCHAR(100),
    region          VARCHAR(100) DEFAULT 'Azerbaijan',
    demand_level    VARCHAR(20),                -- 'high', 'medium', 'low', 'declining'
    growth_rate     DECIMAL(6,2),               -- percentage
    avg_salary_azn  DECIMAL(10,2),
    job_postings    INT,
    data_source     VARCHAR(255),
    observed_at     DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE skill_trends (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name      VARCHAR(255) NOT NULL,
    category        VARCHAR(100),               -- 'technical', 'soft', 'domain'
    demand_level    VARCHAR(20),                -- 'high', 'medium', 'low', 'emerging', 'declining'
    growth_rate     DECIMAL(6,2),
    relevance_to    TEXT[],                     -- array of occupation/sector names
    future_outlook  VARCHAR(20),                -- 'growing', 'stable', 'declining'
    data_source     VARCHAR(255),
    observed_at     DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- ANALYTICS CACHE (precomputed scores)
-- ============================================================

CREATE TABLE analytics_student_scores (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id          UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE UNIQUE,
    institution_id      UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    dropout_risk        DECIMAL(5,2),           -- 0-100
    performance_risk    DECIMAL(5,2),           -- 0-100
    attendance_rate     DECIMAL(5,2),           -- 0-100
    avg_score           DECIMAL(5,2),
    gpa_trend           VARCHAR(20),            -- 'improving', 'stable', 'declining'
    risk_factors        JSONB,                  -- detailed breakdown
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analytics_student_inst ON analytics_student_scores(institution_id);

CREATE TABLE analytics_program_scores (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id              UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE UNIQUE,
    institution_id          UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    performance_score       DECIMAL(5,2),       -- 0-100
    completion_rate         DECIMAL(5,2),
    pass_rate               DECIMAL(5,2),
    avg_gpa                 DECIMAL(4,2),
    dropout_rate            DECIMAL(5,2),
    enrollment_trend        VARCHAR(20),        -- 'growing', 'stable', 'declining'
    relevance_score         DECIMAL(5,2),       -- 0-100 labour market alignment
    demand_trend            VARCHAR(20),        -- 'growing', 'stable', 'declining'
    computed_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analytics_program_inst ON analytics_program_scores(institution_id);

CREATE TABLE analytics_institution_kpis (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id          UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    period                  VARCHAR(20) NOT NULL,  -- '2024-Q1', '2024-01', 'latest'
    total_students          INT,
    active_students         INT,
    total_programs          INT,
    avg_gpa                 DECIMAL(4,2),
    overall_attendance      DECIMAL(5,2),
    overall_pass_rate       DECIMAL(5,2),
    overall_dropout_rate    DECIMAL(5,2),
    at_risk_students        INT,
    high_risk_students      INT,
    avg_program_score       DECIMAL(5,2),
    avg_relevance_score     DECIMAL(5,2),
    computed_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(institution_id, period)
);

-- ============================================================
-- SYNC SYSTEM
-- ============================================================

CREATE TABLE sync_jobs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    source_type     VARCHAR(50) NOT NULL,       -- 'postgresql', 'mysql', 'sqlite', 'api', 'csv'
    connection_config JSONB NOT NULL,           -- encrypted connection details
    tables_to_sync  TEXT[] NOT NULL,            -- which tables to pull
    schedule_cron   VARCHAR(50),               -- cron expression, e.g. '*/15 * * * *'
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sync_job_runs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_job_id     UUID NOT NULL REFERENCES sync_jobs(id) ON DELETE CASCADE,
    status          VARCHAR(30) NOT NULL,       -- 'pending', 'running', 'completed', 'failed', 'partial'
    sync_type       VARCHAR(20) NOT NULL,       -- 'full', 'incremental'
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    records_synced  INT DEFAULT 0,
    records_failed  INT DEFAULT 0,
    error_summary   TEXT,
    duration_ms     INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sync_runs_job ON sync_job_runs(sync_job_id);

CREATE TABLE sync_checkpoints (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_job_id     UUID NOT NULL REFERENCES sync_jobs(id) ON DELETE CASCADE,
    table_name      VARCHAR(100) NOT NULL,
    last_synced_at  TIMESTAMPTZ NOT NULL,
    last_record_id  VARCHAR(100),
    row_count       INT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(sync_job_id, table_name)
);

CREATE TABLE field_mappings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    source_table    VARCHAR(100) NOT NULL,
    source_field    VARCHAR(100) NOT NULL,
    target_table    VARCHAR(100) NOT NULL,
    target_field    VARCHAR(100) NOT NULL,
    transform       VARCHAR(50),               -- 'direct', 'lowercase', 'date_parse', 'map_enum', etc.
    transform_config JSONB,                    -- additional transform params
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE integration_errors (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_job_run_id UUID REFERENCES sync_job_runs(id) ON DELETE SET NULL,
    institution_id  UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    error_type      VARCHAR(50) NOT NULL,       -- 'connection', 'extraction', 'transform', 'load', 'validation'
    source_table    VARCHAR(100),
    source_record_id VARCHAR(100),
    error_message   TEXT NOT NULL,
    error_details   JSONB,
    resolved        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_integration_errors_run ON integration_errors(sync_job_run_id);
CREATE INDEX idx_integration_errors_inst ON integration_errors(institution_id);

-- ============================================================
-- STAGING TABLES (raw data before transformation)
-- ============================================================

CREATE TABLE staging_students (
    id              SERIAL PRIMARY KEY,
    sync_job_run_id UUID NOT NULL REFERENCES sync_job_runs(id),
    institution_id  UUID NOT NULL,
    raw_data        JSONB NOT NULL,
    source_id       VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'processed', 'error'
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE staging_enrollments (
    id              SERIAL PRIMARY KEY,
    sync_job_run_id UUID NOT NULL REFERENCES sync_job_runs(id),
    institution_id  UUID NOT NULL,
    raw_data        JSONB NOT NULL,
    source_id       VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'pending',
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE staging_attendance (
    id              SERIAL PRIMARY KEY,
    sync_job_run_id UUID NOT NULL REFERENCES sync_job_runs(id),
    institution_id  UUID NOT NULL,
    raw_data        JSONB NOT NULL,
    source_id       VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'pending',
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE staging_assessments (
    id              SERIAL PRIMARY KEY,
    sync_job_run_id UUID NOT NULL REFERENCES sync_job_runs(id),
    institution_id  UUID NOT NULL,
    raw_data        JSONB NOT NULL,
    source_id       VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'pending',
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- AUDIT LOG
-- ============================================================

CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id),
    institution_id  UUID REFERENCES institutions(id),
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(50),
    resource_id     UUID,
    details         JSONB,
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_inst ON audit_logs(institution_id);

-- ============================================================
-- SEED: institution types & roles
-- ============================================================

INSERT INTO institution_types (name, display_name) VALUES
    ('university', 'University'),
    ('course_provider', 'Course Provider'),
    ('academy', 'Academy'),
    ('training_center', 'Training Center');

INSERT INTO roles (name, description) VALUES
    ('admin', 'Full access to institution settings, users, and all data'),
    ('analyst', 'Read access to all analytics, limited settings access'),
    ('viewer', 'Read-only access to dashboards and reports');
```

---

## 6. Sync System Design

### Flow Overview

```
PHASE 1: EXTRACT
  Source System (Institution DB)
    → Read-only connection
    → Query by updated_at > last_checkpoint (incremental)
    → OR full table scan (initial sync)
    → Raw records pulled into memory

PHASE 2: STAGE
  Raw records → staging_* tables (JSONB)
    → Each record stored with sync_job_run_id
    → Status: 'pending'

PHASE 3: TRANSFORM
  staging_* tables → validation + field mapping
    → Apply field_mappings for the institution
    → Normalize data types, enums, dates
    → Validate required fields
    → Mark status: 'processed' or 'error'

PHASE 4: LOAD
  Validated records → core tables (UPSERT)
    → Match on (institution_id, source_id)
    → INSERT on new records, UPDATE on existing
    → Update sync_checkpoints with latest updated_at

PHASE 5: AGGREGATE
  Core tables → analytics_* tables
    → Recompute scores for affected students/programs
    → Update KPI cache
    → Generate new recommendations if thresholds crossed
```

### Sync Types

**Full Sync (First-time)**
1. Trigger: manual or on first connection
2. Extracts all records from source tables
3. Loads through full staging → transform → load pipeline
4. Sets initial checkpoint values
5. Expected duration: seconds for MVP data volumes

**Incremental Sync (Scheduled)**
1. Trigger: Celery Beat on cron schedule
2. Reads checkpoint: `last_synced_at` per table
3. Queries source: `WHERE updated_at > :checkpoint`
4. Processes only changed/new records
5. Updates checkpoint on success
6. Typical volume: 10-100 records per run

### Schedule Configuration

| Data Type | Cron | Frequency |
|---|---|---|
| Students, enrollments | `*/15 * * * *` | Every 15 minutes |
| Attendance, assessments | `*/10 * * * *` | Every 10 minutes |
| KPI aggregation | `*/30 * * * *` | Every 30 minutes |
| Labour market data | `0 3 * * *` | Daily at 3 AM |
| Forecasting refresh | `0 4 * * *` | Daily at 4 AM |
| Recommendations | `0 5 * * *` | Daily at 5 AM |

### Retry Logic
- Failed sync runs are retried up to 3 times with exponential backoff (30s, 120s, 480s)
- After 3 failures, sync job is marked `failed` and an integration_error is logged
- Admin is notified (sync status shows failure on dashboard)
- Next scheduled run proceeds independently

### Error Handling
- **Connection errors** → retry with backoff, log to integration_errors
- **Extraction errors** → skip problematic record, continue with rest, log error
- **Transform errors** → mark staging record as 'error', continue with rest
- **Load errors** → rollback individual record, log error, continue
- **Partial success** → sync_job_run status = 'partial', records_failed > 0

### Mock Source Design (MVP)
For the hackathon, each institution gets a SQLite database that simulates their source system:

```
mock-sources/
├── university/
│   └── source.db          # SQLite with students, programs, etc.
├── course_provider/
│   └── source.db
└── seed_mock_data.py      # Script to generate realistic data
```

The sync engine connects to these SQLite DBs using the same interface it would use for real PostgreSQL/MySQL connections, proving the architecture works.

---

## 7. API Design

### Base URL: `/api/v1`

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register institution + admin user |
| POST | `/auth/login` | Login, returns JWT access + refresh tokens |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Current user profile |
| PUT | `/auth/me` | Update profile |

### Institutions
| Method | Endpoint | Description |
|---|---|---|
| GET | `/institutions/me` | Current institution profile |
| PUT | `/institutions/me` | Update institution profile |
| GET | `/institutions/me/stats` | Quick stats summary |

### Students
| Method | Endpoint | Description |
|---|---|---|
| GET | `/students` | List students (paginated, filterable) |
| GET | `/students/:id` | Student detail |
| GET | `/students/:id/attendance` | Student attendance history |
| GET | `/students/:id/assessments` | Student assessment history |
| GET | `/students/:id/risk` | Student risk detail with factors |
| GET | `/students/at-risk` | All at-risk students sorted by risk score |

**Filters**: `?program_id=`, `?status=`, `?risk_level=`, `?semester=`, `?search=`

### Programs & Courses
| Method | Endpoint | Description |
|---|---|---|
| GET | `/programs` | List programs with scores |
| GET | `/programs/:id` | Program detail with analytics |
| GET | `/programs/:id/courses` | Courses in program |
| GET | `/programs/:id/students` | Students in program |
| GET | `/programs/comparison` | Side-by-side program comparison |
| GET | `/courses` | List all courses |
| GET | `/courses/:id` | Course detail |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/dashboard` | Full dashboard payload (KPIs, charts, alerts) |
| GET | `/analytics/kpis` | Current KPI values |
| GET | `/analytics/enrollment-trend` | Enrollment over time |
| GET | `/analytics/attendance-trend` | Attendance over time |
| GET | `/analytics/dropout-trend` | Dropout rates over time |
| GET | `/analytics/cohort/:year` | Cohort analysis for enrollment year |
| GET | `/analytics/performance-distribution` | Score/GPA distribution |

### Sync
| Method | Endpoint | Description |
|---|---|---|
| GET | `/sync/jobs` | List configured sync jobs |
| POST | `/sync/jobs` | Create sync job |
| PUT | `/sync/jobs/:id` | Update sync job |
| POST | `/sync/jobs/:id/trigger` | Manually trigger sync |
| GET | `/sync/jobs/:id/runs` | List sync run history |
| GET | `/sync/runs/:id` | Sync run detail |
| GET | `/sync/status` | Overall sync health summary |
| GET | `/sync/errors` | Recent integration errors |

### Recommendations
| Method | Endpoint | Description |
|---|---|---|
| GET | `/recommendations` | List recommendations (filterable by level, category) |
| GET | `/recommendations/:id` | Recommendation detail |
| PUT | `/recommendations/:id/status` | Accept/dismiss recommendation |
| POST | `/recommendations/generate` | Trigger recommendation refresh |

### Forecasts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/forecasts/enrollment` | Predicted enrollment by program |
| GET | `/forecasts/dropout` | Predicted dropout rates |
| GET | `/forecasts/demand` | Predicted program demand |

### Skills & Labour Market
| Method | Endpoint | Description |
|---|---|---|
| GET | `/labour-market/trends` | Current occupation demand trends |
| GET | `/labour-market/skills` | In-demand skills |
| GET | `/labour-market/alignment` | Program-to-market alignment scores |
| GET | `/labour-market/declining` | Declining professions/skills |
| GET | `/labour-market/emerging` | Emerging skills/sectors |

### Settings
| Method | Endpoint | Description |
|---|---|---|
| GET | `/settings/users` | List institution users |
| POST | `/settings/users` | Invite user |
| PUT | `/settings/users/:id` | Update user role |
| DELETE | `/settings/users/:id` | Deactivate user |
| GET | `/settings/audit-log` | Audit log entries |
| GET | `/settings/field-mappings` | Current field mappings |
| PUT | `/settings/field-mappings` | Update field mappings |

---

## 8. Frontend Structure

### Page Structure (Next.js App Router)

```
src/app/
├── (public)/                          # Public pages (no auth required)
│   ├── page.tsx                       # Landing page
│   ├── login/page.tsx                 # Login
│   ├── register/page.tsx              # Register / request demo
│   └── layout.tsx                     # Public layout (minimal header)
│
├── (platform)/                        # Authenticated platform
│   ├── layout.tsx                     # Platform layout (sidebar + header)
│   ├── dashboard/page.tsx             # Overview dashboard
│   ├── students/
│   │   ├── page.tsx                   # Student risk list
│   │   └── [id]/page.tsx             # Student detail
│   ├── programs/
│   │   ├── page.tsx                   # Program analytics
│   │   ├── [id]/page.tsx             # Program detail
│   │   └── compare/page.tsx          # Program comparison
│   ├── skills/page.tsx                # Skills & labour market
│   ├── recommendations/page.tsx       # Recommendations
│   ├── forecasts/page.tsx             # Forecasting
│   └── settings/
│       ├── page.tsx                   # Institution profile
│       ├── integrations/page.tsx      # Sync / data source config
│       ├── users/page.tsx             # User management
│       └── logs/page.tsx              # Audit & sync logs
│
├── api/                               # BFF routes (optional proxy)
└── layout.tsx                         # Root layout
```

### Component Structure

```
src/components/
├── ui/                                # Base components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Badge.tsx
│   ├── Table.tsx
│   ├── Modal.tsx
│   ├── Input.tsx
│   ├── Select.tsx
│   ├── Tabs.tsx
│   ├── Skeleton.tsx                   # Loading skeletons
│   └── EmptyState.tsx
│
├── charts/                            # Chart components
│   ├── AreaChart.tsx                   # Enrollment/attendance trends
│   ├── BarChart.tsx                    # Program comparison
│   ├── DonutChart.tsx                  # Distribution (pass/fail)
│   ├── LineChart.tsx                   # Time series (GPA trend)
│   ├── HeatMap.tsx                     # Attendance heatmap
│   └── ScatterPlot.tsx                # Attendance vs performance
│
├── dashboard/                         # Dashboard-specific
│   ├── KPICard.tsx                    # Single KPI with trend indicator
│   ├── KPIGrid.tsx                    # Grid of KPI cards
│   ├── RiskSummary.tsx                # At-risk students summary
│   ├── TopPrograms.tsx                # Top/bottom programs widget
│   ├── RecentAlerts.tsx               # Recent warnings/alerts
│   └── QuickRecommendations.tsx       # Top recommendation cards
│
├── students/
│   ├── StudentTable.tsx               # Sortable/filterable student table
│   ├── RiskBadge.tsx                  # Color-coded risk level
│   ├── RiskFactors.tsx                # Risk breakdown component
│   ├── AttendanceChart.tsx            # Per-student attendance
│   └── PerformanceTimeline.tsx        # GPA/score over time
│
├── programs/
│   ├── ProgramCard.tsx                # Program summary card
│   ├── ProgramComparisonTable.tsx     # Side-by-side metrics
│   ├── CompletionRateChart.tsx
│   └── DemandTrendChart.tsx
│
├── skills/
│   ├── SkillDemandChart.tsx           # Skills demand visualization
│   ├── AlignmentScoreCard.tsx         # Program alignment score
│   ├── DecliningSkillsList.tsx
│   └── EmergingSkillsList.tsx
│
├── recommendations/
│   ├── RecommendationCard.tsx         # Individual recommendation
│   ├── RecommendationList.tsx         # Filtered list
│   └── PriorityBadge.tsx
│
├── layout/
│   ├── Sidebar.tsx                    # Navigation sidebar
│   ├── Header.tsx                     # Top header with user menu
│   ├── InstitutionSelector.tsx        # (future: multi-institution)
│   └── BreadCrumbs.tsx
│
└── landing/
    ├── Hero.tsx
    ├── Features.tsx
    ├── HowItWorks.tsx
    ├── CTASection.tsx
    └── Footer.tsx
```

---

## 9. UX Recommendations

### Design Direction
- **Style**: Clean, professional, data-dense but not cluttered
- **Color palette**: Deep blue primary (#1e3a5f), teal accent (#0ea5e9), white/light gray backgrounds
- **Risk colors**: Red (#ef4444) high risk, amber (#f59e0b) medium, green (#22c55e) low
- **Font**: Inter for UI, monospace for data values
- **Spacing**: Generous whitespace between sections, compact within data tables

### Dashboard Layout
```
┌──────────────────────────────────────────────────────────┐
│ Header: Logo | Institution Name | Search | User Menu     │
├──────────┬───────────────────────────────────────────────┤
│          │  KPI Cards (4 across)                         │
│ Sidebar  │  [Students] [Attendance] [Pass Rate] [Risk]   │
│          ├───────────────────┬───────────────────────────┤
│ Dashboard│  Enrollment Trend │  Risk Distribution        │
│ Students │  (area chart)     │  (donut chart)            │
│ Programs ├───────────────────┴───────────────────────────┤
│ Skills   │  Programs Performance Table                   │
│ Recom.   │  (sortable, with score bars)                  │
│ Forecast ├───────────────────────────────────────────────┤
│ Settings │  Recent Alerts  │  Top Recommendations        │
│          │  (list)         │  (cards)                     │
└──────────┴───────────────────────────────────────────────┘
```

### Navigation
- Left sidebar: icon + label, collapsible to icons only
- Active state: highlighted background + left border accent
- Breadcrumbs for drill-down pages (Dashboard > Students > Student Name)
- Keyboard shortcut hints for power users

### Cards & KPIs
- KPI cards: large number, label below, trend arrow (up/down) with percentage change
- Color-coded left border indicating status (green/amber/red)
- Sparkline mini-chart in KPI card footer showing 30-day trend

### Tables
- Sticky header, horizontal scroll on mobile
- Sortable columns (click header)
- Filter row above table: dropdowns for program, status, risk level
- Search input for name/code lookup
- Inline risk badge (colored dot + label)
- Row click navigates to detail page

### Charts
- Consistent color scheme across all charts
- Tooltips on hover with exact values
- Time range selector: 7d, 30d, 90d, 1y, All
- Legend positioned below chart, toggleable series

### Warning States
- High-risk students: red card border, red badge, alert icon
- Declining programs: amber highlight in program table
- Sync failures: red banner at top of dashboard with "last successful sync" time
- Empty states: illustration + helpful message + action button

### Recommendation Presentation
- Card layout with priority badge (High / Medium / Low)
- Category icon (curriculum, intervention, resource)
- "AI-generated" label where applicable
- Action buttons: Accept / Dismiss / View Details
- Expandable detail section with supporting data

---

## 10. Simulated Demo Data Plan

### Institution 1: Baku State Technical University (mock)

| Attribute | Value |
|---|---|
| Type | University |
| Programs | 5 (Computer Science, Business Admin, Civil Engineering, Medicine, Azerbaijani Language & Literature) |
| Students | ~600 across all programs |
| Semesters | 8 (4-year bachelor) |
| Courses per program | 6-8 |

**Data Patterns**:

| Pattern | Implementation |
|---|---|
| CS enrollment growing 15% year-over-year | More recent enrollment dates in CS program |
| Language & Literature declining 10% YoY | Fewer recent enrollments, more drops |
| First-year dropout ~15%, fourth-year ~2% | Dropout events concentrated in semester 1-2 students |
| Attendance-performance correlation | Students with <70% attendance have avg GPA 1.5 lower |
| Engineering high difficulty | Lower avg scores but higher employment alignment |
| Medicine high completion | 95% completion rate, strict attendance |
| Some students at risk | ~8% of active students have high dropout risk signals |

**Sample Student Profiles**:
- "Exemplary CS student": 95% attendance, 3.8 GPA, improving trend
- "At-risk first-year": 60% attendance, 1.9 GPA, 3 missed assessments → high dropout risk
- "Recovering student": dropped attendance to 65%, now back to 85% after intervention
- "Quiet decline": attendance 80% but GPA dropped from 3.2 to 2.4 over 3 semesters

### Institution 2: Azerbaijan Digital Academy (mock)

| Attribute | Value |
|---|---|
| Type | Course Provider |
| Programs | 8 (Web Development, Data Science, Digital Marketing, UI/UX Design, Cybersecurity, Cloud Computing, Project Management, AI/ML Fundamentals) |
| Students | ~250 across all programs |
| Duration | 3-6 months per program |
| Courses per program | 4-6 modules |

**Data Patterns**:

| Pattern | Implementation |
|---|---|
| Data Science and AI/ML booming | Highest enrollment, growing demand |
| Digital Marketing saturating | Flat enrollment, medium market demand |
| Project Management low engagement | Lower completion rate, lower attendance |
| Web Development solid and stable | High completion, consistent demand |
| First-month dropout 20% | Many drops in first 2-4 weeks |
| Cybersecurity growing fast | Small cohorts but rapid growth |
| Strong labour market alignment | Tech courses match well with job postings |

### Labour Market Demo Data

| Occupation/Sector | Demand | Growth | Notes |
|---|---|---|---|
| Software Development | High | +22% | Strong match to CS and Web Dev |
| Data Analysis/Science | High | +30% | Emerging, few programs cover it |
| Cybersecurity | High | +25% | Critical gap in local talent |
| Digital Marketing | Medium | +5% | Saturating, needs specialization |
| Civil Engineering | Medium | +8% | Stable, infrastructure projects |
| Traditional Admin | Low | -10% | Declining, automation replacing |
| Language Teaching | Low | -5% | Limited market growth |
| Cloud/DevOps | High | +28% | Few local training options |
| Healthcare/Medicine | High | +12% | Steady demand |
| AI/ML Engineering | High | +35% | Nascent but fastest growing |

### Skills Demo Data
- High demand: Python, SQL, data visualization, cloud platforms, project management
- Emerging: machine learning, DevOps, UX research, API design
- Declining: manual data entry, basic office suite, traditional bookkeeping

---

## 11. Analytics & Scoring Logic

### Dropout Risk Score (0-100)

Higher score = higher risk of dropping out.

```
dropout_risk = (
    w1 * attendance_factor +
    w2 * performance_factor +
    w3 * assessment_completion_factor +
    w4 * semester_factor +
    w5 * trend_factor
)

Weights:
  w1 = 0.30  (attendance)
  w2 = 0.25  (academic performance)
  w3 = 0.20  (assessment engagement)
  w4 = 0.10  (year/semester — first-year higher baseline)
  w5 = 0.15  (recent trajectory)

attendance_factor:
  rate >= 90%  → 0
  rate 80-89%  → 20
  rate 70-79%  → 45
  rate 60-69%  → 70
  rate < 60%   → 95

performance_factor:
  gpa >= 3.5   → 0
  gpa 3.0-3.49 → 15
  gpa 2.5-2.99 → 35
  gpa 2.0-2.49 → 60
  gpa < 2.0    → 90

assessment_completion_factor:
  completion >= 95%  → 0
  completion 85-94%  → 20
  completion 70-84%  → 50
  completion < 70%   → 85

semester_factor:
  semester 1    → 60 (highest baseline risk)
  semester 2    → 40
  semester 3-4  → 20
  semester 5+   → 10

trend_factor (GPA change over last 2 periods):
  improving (>+0.3)  → 0
  stable (±0.3)      → 25
  declining (>-0.3)  → 60
  sharp decline (>-0.6) → 90
```

**Risk Levels**: High >= 70, Medium 40-69, Low < 40

### Low-Performance Risk Score (0-100)

```
performance_risk = (
    0.35 * gpa_deviation +
    0.30 * recent_scores +
    0.20 * attendance_penalty +
    0.15 * failed_assessments
)

gpa_deviation:
  GPA >= program avg       → 0
  GPA 0.5 below avg        → 30
  GPA 1.0 below avg        → 60
  GPA 1.5+ below avg       → 90

recent_scores (last 5 assessments avg):
  >= 80%  → 0
  70-79%  → 25
  60-69%  → 50
  50-59%  → 75
  < 50%   → 95

attendance_penalty:
  >= 85%  → 0
  75-84%  → 20
  65-74%  → 50
  < 65%   → 80

failed_assessments (% of assessments with score < 50%):
  0%      → 0
  1-10%   → 20
  11-25%  → 50
  > 25%   → 85
```

### Program Performance Score (0-100)

Higher score = better performing program.

```
program_score = (
    0.25 * completion_rate_normalized +
    0.20 * avg_gpa_normalized +
    0.20 * pass_rate_normalized +
    0.20 * market_alignment +
    0.15 * enrollment_health
)

completion_rate_normalized:   (completion_rate / 100) * 100
pass_rate_normalized:         (pass_rate / 100) * 100
avg_gpa_normalized:           (avg_gpa / 4.0) * 100
market_alignment:             relevance_score (from labour market alignment)
enrollment_health:
  growing   → 80
  stable    → 60
  declining → 30
```

### Course Relevance Score (0-100)

```
relevance_score = (
    0.35 * demand_match +
    0.25 * future_demand +
    0.20 * enrollment_trend +
    0.20 * completion_signal
)

demand_match:
  Map course skills/keywords to labour_market_trends
  high demand match    → 90
  medium demand match  → 60
  low demand match     → 30
  no match / declining → 10

future_demand:
  Map to skill_trends future_outlook
  growing    → 90
  stable     → 50
  declining  → 15

enrollment_trend:
  growing    → 85
  stable     → 55
  declining  → 20

completion_signal:
  > 85% completion → 80
  70-85%           → 55
  < 70%            → 25
```

### Labour Market Alignment Score (0-100)

Per-program score comparing what the program teaches to what the market demands.

```
alignment_score = (
    0.40 * skills_overlap +
    0.30 * sector_growth +
    0.30 * demand_level
)

skills_overlap:
  % of program's tagged skills that appear in high/emerging skill_trends
  > 70% overlap → 90
  50-70%        → 65
  30-49%        → 40
  < 30%         → 15

sector_growth:
  Avg growth_rate of matching labour_market_trends
  > 20%  → 90
  10-20% → 65
  0-10%  → 40
  < 0%   → 15

demand_level:
  high      → 90
  medium    → 55
  low       → 25
  declining → 10
```

### Recommendation Priority Score (0-100)

```
priority = (
    0.30 * impact +
    0.30 * urgency +
    0.20 * feasibility +
    0.20 * confidence
)

impact: estimated number of students affected, normalized to 0-100
urgency: based on risk levels and trend direction
feasibility: rule-based (curriculum change = 50, intervention = 80, new program = 30)
confidence: based on data completeness and sample size
```

---

## 12. AI Usage Plan

### Principle
AI augments human decision-making. It does **not** compute core metrics (those are deterministic algorithms above). AI is used for interpretation, natural language, and suggestion generation.

### Use Cases

| Use Case | Input | Output | Model |
|---|---|---|---|
| **Analytics Summary** | KPI values, trends, risk counts | 2-3 sentence natural language summary for dashboard | Claude API |
| **Risk Explanation** | Student risk factors JSON | "This student's dropout risk is high because attendance dropped 25% in the last month and GPA declined from 3.1 to 2.3." | Claude API |
| **Program Recommendation** | Program scores, market data | "Consider adding a Data Science specialization track. Market demand is growing 30% YoY and your CS program already covers 60% of prerequisite skills." | Claude API |
| **Curriculum Suggestion** | Skills gap analysis | List of specific skills/modules to add or update in a program | Claude API |
| **Intervention Suggestion** | At-risk student patterns | Suggested intervention steps for student advisors | Claude API |
| **Report Generation** | All analytics for a period | Formatted executive summary report | Claude API |

### Safety Guardrails
1. All AI-generated content is clearly labeled with an "AI-generated" badge
2. Core scores and KPIs are never computed by AI — only deterministic algorithms
3. AI recommendations include "supporting data" section showing the analytics that led to the suggestion
4. Users can dismiss or accept recommendations — AI never auto-executes actions
5. AI prompts include institution context but never raw student PII (use aggregated/anonymized data)
6. Rate limiting on AI calls to control costs (batch recommendations daily, not per-request)

### Implementation
```python
# Example: Generate risk explanation
async def explain_risk(student_scores: dict) -> str:
    prompt = f"""You are an education analytics assistant.
    Given these risk factors for a student, provide a brief,
    clear explanation of why they are at risk.

    Risk Factors: {json.dumps(student_scores['risk_factors'])}
    Dropout Risk Score: {student_scores['dropout_risk']}/100
    Attendance Rate: {student_scores['attendance_rate']}%
    GPA Trend: {student_scores['gpa_trend']}

    Write 2-3 sentences. Be specific and actionable."""

    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

## 13. Folder Structure / Project Structure

```
dds-gui/
│
├── frontend/                          # Next.js 14 application
│   ├── src/
│   │   ├── app/                       # App Router pages (see Section 8)
│   │   ├── components/                # React components (see Section 8)
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client (fetch wrapper)
│   │   │   ├── auth.ts                # Token management
│   │   │   └── utils.ts               # Formatting, helpers
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useDashboard.ts
│   │   │   └── useStudents.ts
│   │   ├── types/
│   │   │   ├── api.ts                 # API response types
│   │   │   ├── models.ts              # Domain model types
│   │   │   └── charts.ts              # Chart data types
│   │   └── styles/
│   │       └── globals.css
│   ├── public/
│   │   └── images/
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                           # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings (env vars, DB URL, etc.)
│   │   ├── database.py                # SQLAlchemy engine & session
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # Dependency injection (auth, db session)
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── institutions.py
│   │   │       ├── students.py
│   │   │       ├── programs.py
│   │   │       ├── analytics.py
│   │   │       ├── sync.py
│   │   │       ├── recommendations.py
│   │   │       ├── forecasts.py
│   │   │       ├── labour_market.py
│   │   │       └── settings.py
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── institution.py
│   │   │   ├── user.py
│   │   │   ├── student.py
│   │   │   ├── program.py
│   │   │   ├── course.py
│   │   │   ├── enrollment.py
│   │   │   ├── attendance.py
│   │   │   ├── assessment.py
│   │   │   ├── analytics.py
│   │   │   ├── recommendation.py
│   │   │   ├── labour_market.py
│   │   │   └── sync.py
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── student.py
│   │   │   ├── program.py
│   │   │   ├── analytics.py
│   │   │   ├── sync.py
│   │   │   └── recommendation.py
│   │   ├── services/                  # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── student_service.py
│   │   │   ├── program_service.py
│   │   │   └── analytics_service.py
│   │   ├── sync/                      # Sync engine
│   │   │   ├── __init__.py
│   │   │   ├── engine.py              # Orchestrates full/incremental sync
│   │   │   ├── extractors/
│   │   │   │   ├── base.py            # Abstract extractor interface
│   │   │   │   ├── sqlite.py          # SQLite extractor (MVP)
│   │   │   │   └── postgresql.py      # PostgreSQL extractor (future)
│   │   │   ├── transformers/
│   │   │   │   ├── base.py
│   │   │   │   ├── student.py
│   │   │   │   ├── enrollment.py
│   │   │   │   └── attendance.py
│   │   │   └── loaders/
│   │   │       ├── base.py
│   │   │       └── postgres_loader.py
│   │   ├── analytics/                 # Scoring algorithms
│   │   │   ├── __init__.py
│   │   │   ├── dropout_risk.py
│   │   │   ├── performance_risk.py
│   │   │   ├── program_score.py
│   │   │   ├── relevance_score.py
│   │   │   └── aggregator.py          # KPI aggregation
│   │   ├── ai/                        # AI/LLM integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py              # Claude API client
│   │   │   ├── prompts.py             # Prompt templates
│   │   │   └── recommendations.py     # AI recommendation generation
│   │   └── tasks/                     # Celery tasks
│   │       ├── __init__.py
│   │       ├── celery_app.py          # Celery config
│   │       ├── sync_tasks.py          # Sync job tasks
│   │       ├── analytics_tasks.py     # Score computation tasks
│   │       └── ai_tasks.py            # AI generation tasks
│   ├── migrations/                    # Alembic
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── seeds/
│   │   ├── seed_demo.py               # Seed platform DB with demo data
│   │   └── seed_labour_market.py      # Seed external data
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── mock-sources/                      # Simulated institution databases
│   ├── university/
│   │   └── source.db                  # SQLite (Baku State Technical mock)
│   ├── course_provider/
│   │   └── source.db                  # SQLite (Azerbaijan Digital Academy mock)
│   ├── generate_mock_data.py          # Script to generate realistic mock data
│   └── schemas/
│       ├── university_schema.sql      # Source system schema for university
│       └── provider_schema.sql        # Source system schema for course provider
│
├── docker-compose.yml                 # PostgreSQL + Redis + Backend + Celery + Frontend
├── .env.example
├── .gitignore
└── README.md
```

---

## 14. Two-Week Hackathon / MVP Plan

### Week 1: Core System

| Day | Focus | Deliverables |
|---|---|---|
| **Day 1** | Project Setup | Monorepo scaffold, Docker Compose (PostgreSQL + Redis), environment config, Git repo |
| **Day 2** | Database & Models | PostgreSQL schema migration, all SQLAlchemy models, seed institution types & roles |
| **Day 3** | Mock Sources & Seed Data | SQLite mock databases for university + course provider, realistic data generation script (~600 + ~250 students) |
| **Day 4** | Sync Engine | Full sync: extract → stage → transform → load pipeline, working end-to-end for both institutions |
| **Day 5** | Incremental Sync | Checkpoint-based incremental sync, Celery Beat schedule, retry logic, sync logging |
| **Day 6** | Auth & Core APIs | JWT auth (register/login/refresh), institution endpoints, student/program CRUD with pagination & filters |
| **Day 7** | Analytics Engine | All scoring algorithms implemented, analytics aggregation Celery tasks, analytics API endpoints, KPI computation |

### Week 2: UI & Polish

| Day | Focus | Deliverables |
|---|---|---|
| **Day 8** | Frontend Foundation | Next.js setup, Tailwind + Tremor, auth pages (login/register), platform layout (sidebar, header), API client |
| **Day 9** | Dashboard | KPI cards, enrollment trend chart, risk summary donut, top programs table, recent alerts |
| **Day 10** | Student Analytics | Student risk list with filters, student detail page, attendance-performance scatter plot, risk factor breakdown |
| **Day 11** | Program & Skills | Program comparison table, completion/pass rates, skills demand charts, labour market alignment scores, declining professions |
| **Day 12** | Recommendations & Forecasts | Recommendation cards with AI explanations, forecast charts (enrollment/dropout predictions), AI integration |
| **Day 13** | Landing & Settings | Public landing page, settings page (institution profile, sync status, user roles, sync logs) |
| **Day 14** | Polish & Demo Prep | End-to-end testing, loading/error states, demo script rehearsal, final UI polish, README documentation |

---

## 15. Final Recommendation

### Recommended Architecture
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + Tremor + Recharts
- **Backend**: FastAPI (Python 3.11+) + SQLAlchemy 2.0 + Pydantic v2
- **Database**: PostgreSQL 16 with staging + core + analytics table layers
- **Task Queue**: Celery + Redis (sync, analytics, AI tasks)
- **AI**: Claude API (Sonnet for speed/cost, summaries and recommendations only)
- **Auth**: JWT with bcrypt, role-based access
- **Deployment (MVP)**: Docker Compose (all services)

### Why This Stack
1. **Python backend** is the right call for a data-heavy analytics platform — pandas, numpy, and the AI SDK ecosystem are unmatched
2. **FastAPI** gives you automatic OpenAPI docs, async support, and fastest development speed
3. **Next.js App Router** with Tremor gives production-quality dashboard UI with minimal custom code
4. **Celery** handles all async work (sync, analytics, AI) without architectural complexity
5. **PostgreSQL** handles everything from JSONB staging to analytical queries to full-text search

### What Makes This MVP Credible
- Real sync engine (not fake data refresh)
- Deterministic analytics (not AI guessing)
- AI used appropriately (explanations, not calculations)
- Near-real-time feel through scheduled incremental sync
- Two distinct institution types proving platform flexibility

---

## A. Best MVP Version (Minimum Viable Demo)

If time is extremely tight, cut to this core:

| Include | Cut |
|---|---|
| Auth (login only, pre-seeded users) | Registration flow |
| Dashboard with KPIs | Forecasting page |
| Student risk list + detail | Cohort analysis |
| Program analytics table | Program comparison page |
| Skills alignment (static data) | Real-time external data ingestion |
| Top 5 AI recommendations | Full recommendation management |
| Sync status display | Sync configuration UI |
| Pre-seeded demo data | Data generation scripts |

**Minimum pages**: Login → Dashboard → Students → Programs → Skills → Recommendations (6 pages total)

---

## B. Best Demo Flow

**Duration**: 8-10 minutes

1. **Landing page** (30s) — "This is EduScope — Azerbaijan's first Higher Education Intelligence Platform."

2. **Login as university admin** (15s) — Pre-filled credentials, instant login.

3. **Dashboard** (90s) — "Here's Baku State Technical University at a glance. 587 active students, 92% attendance, but notice: 47 students flagged as at-risk — that's 8% of our student body."

4. **Student Risk drill-down** (90s) — "Let's look at the at-risk list. This first-year CS student has attendance dropping to 62% over the last month, GPA declined from 2.8 to 2.1. The system detected this automatically from the last sync 12 minutes ago."

5. **Individual student detail** (60s) — "Here's the full picture: attendance heatmap, grade trajectory, risk factor breakdown. The platform recommends immediate advisor outreach."

6. **Program Analytics** (60s) — "Computer Science is our strongest program: 89% completion, growing enrollment. But look at Language & Literature — 61% completion, declining enrollment, and low market alignment."

7. **Skills & Labour Market** (60s) — "The platform continuously maps programs to market demand. Data Science skills are growing 30% year-over-year, but we have no Data Science program. Cybersecurity demand is surging with few local training options."

8. **Recommendations** (60s) — "Based on all this data, the platform's top recommendation: launch a Data Science specialization. It shows the supporting evidence and estimated impact."

9. **Switch to Course Provider** (60s) — "Now let's see Azerbaijan Digital Academy — same platform, different institution type. Their Web Development bootcamp has 94% completion, but Project Management is struggling at 67%. Different context, same analytical power."

10. **Sync demonstration** (30s) — "Everything you've seen updates automatically. The last sync was 8 minutes ago, pulling only new and changed records. No manual uploads needed."

11. **Close** (30s) — "This is the future of education analytics in Azerbaijan — data-driven, automated, and actionable."

---

## C. What to Build First This Week

### Day 1 Checklist
- [ ] Initialize monorepo: `frontend/`, `backend/`, `mock-sources/`
- [ ] Create `docker-compose.yml` with PostgreSQL 16 + Redis 7
- [ ] Set up FastAPI project with `requirements.txt`
- [ ] Set up Next.js 14 project with TypeScript + Tailwind + Tremor
- [ ] Create `.env.example` with all config vars
- [ ] Run `docker-compose up` and verify services start

### Day 2 Checklist
- [ ] Write full PostgreSQL schema (Section 5 above)
- [ ] Set up Alembic and create initial migration
- [ ] Create all SQLAlchemy models
- [ ] Run migration, verify all tables created
- [ ] Seed institution_types and roles
- [ ] Create 2 demo institutions (university + course provider)

### Day 3 Checklist
- [ ] Design mock source SQLite schemas (simpler than platform schema)
- [ ] Write `generate_mock_data.py` with realistic patterns from Section 10
- [ ] Generate ~600 university students + ~250 course provider students
- [ ] Verify mock databases have realistic attendance-performance correlation
- [ ] Verify dropout patterns match expectations

### Day 4 Checklist
- [ ] Implement sync engine: extractor → stager → transformer → loader
- [ ] Run full sync from both mock sources to platform DB
- [ ] Verify data appears correctly in core tables
- [ ] Implement sync_job_runs logging
- [ ] Set up Celery + Celery Beat
- [ ] Configure incremental sync on 15-minute schedule

### Day 5 Checklist
- [ ] Implement JWT auth endpoints (register, login, refresh, me)
- [ ] Implement student list API with pagination + filters
- [ ] Implement program list API
- [ ] Implement basic analytics/KPI endpoint
- [ ] Test all endpoints with curl/httpie
- [ ] Verify auth middleware works correctly
