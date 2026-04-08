import uuid
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from slugify import slugify

from app.api.deps import DB, CurrentUser, hash_password, verify_password, create_access_token, create_refresh_token
from app.config import get_settings
from app.models.institution import Institution, InstitutionType
from app.models.user import User, Role
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _make_slug(name: str) -> str:
    # Simple slug: lowercase, replace spaces with hyphens
    return name.lower().replace(" ", "-").replace("&", "and")[:100]


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: DB):
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Find institution type
    inst_type = await db.execute(
        select(InstitutionType).where(InstitutionType.name == req.institution_type)
    )
    inst_type = inst_type.scalar_one_or_none()
    if not inst_type:
        raise HTTPException(status_code=400, detail=f"Invalid institution type: {req.institution_type}")

    # Create institution
    institution = Institution(
        name=req.institution_name,
        type_id=inst_type.id,
        slug=_make_slug(req.institution_name) + "-" + uuid.uuid4().hex[:6],
    )
    db.add(institution)
    await db.flush()

    # Get admin role
    admin_role = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = admin_role.scalar_one()

    # Create admin user
    user = User(
        institution_id=institution.id,
        role_id=admin_role.id,
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
    )
    db.add(user)
    await db.commit()

    return TokenResponse(
        access_token=create_access_token(str(user.id), str(institution.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: DB):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return TokenResponse(
        access_token=create_access_token(str(user.id), str(user.institution_id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest, db: DB):
    try:
        payload = jwt.decode(req.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(str(user.id), str(user.institution_id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser, db: DB):
    await db.refresh(user, ["role", "institution"])
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        institution_id=user.institution_id,
        institution_name=user.institution.name,
    )
