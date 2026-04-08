# EduScope — Higher Education Intelligence Platform

Analytics platform for universities and course providers in Azerbaijan.

## Quick Start

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Seed the database (creates platform.db with demo data)
python -m seeds.seed_demo

# 3. Start the backend
python -m uvicorn app.main:app --port 8000

# 4. In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and log in:
- **University**: admin@beu.edu.az / demo123
- **Course provider**: admin@digitalacademy.az / demo123
