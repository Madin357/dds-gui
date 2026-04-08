from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, students, programs, analytics, sync_routes, recommendations

app = FastAPI(
    title="EduScope - Higher Education Intelligence Platform",
    description="Analytics platform for universities and course providers in Azerbaijan",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes under /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(programs.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(sync_routes.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "eduscope"}
