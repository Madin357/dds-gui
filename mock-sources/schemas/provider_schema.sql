-- Mock source schema for a course provider LMS (Learning Management System)
-- Shorter courses, module-based structure

CREATE TABLE programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT,
    category TEXT,
    duration_weeks INTEGER DEFAULT 12,
    is_active INTEGER DEFAULT 1,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER REFERENCES programs(id),
    name TEXT NOT NULL,
    code TEXT,
    module_number INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    date_of_birth TEXT,
    gender TEXT,
    enrollment_date TEXT,
    status TEXT DEFAULT 'active',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    program_id INTEGER REFERENCES programs(id),
    status TEXT DEFAULT 'active',
    enrolled_at TEXT NOT NULL,
    completed_at TEXT,
    dropped_at TEXT,
    drop_reason TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    session_date TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    type TEXT NOT NULL,
    title TEXT,
    score REAL,
    max_score REAL DEFAULT 100,
    grade TEXT,
    assessed_at TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
