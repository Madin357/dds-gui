from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="EduScope - Higher Education Intelligence Platform",
    description="Analytics platform for universities and course providers in Azerbaijan",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.DEMO_MODE:
    # Demo mode: serve in-memory mock data, no database required
    from app.demo.routes import mount_demo_routes
    mount_demo_routes(app)

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "service": "eduscope", "mode": "demo"}
else:
    # Production mode: database-backed routes
    from sqlalchemy import text
    from app.api.routes import auth, students, programs, analytics, sync_routes, recommendations

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(students.router, prefix="/api/v1")
    app.include_router(programs.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(sync_routes.router, prefix="/api/v1")
    app.include_router(recommendations.router, prefix="/api/v1")

    @app.get("/api/health")
    async def health_check():
        from app.database import async_engine
        db_ok = True
        try:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:
            db_ok = False
        return {
            "status": "ok" if db_ok else "degraded",
            "service": "eduscope",
            "database": "connected" if db_ok else "unreachable",
        }
