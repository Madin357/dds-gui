from pydantic import BaseModel, EmailStr
import uuid


class RegisterRequest(BaseModel):
    institution_name: str
    institution_type: str  # 'university', 'course_provider', etc.
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    institution_id: uuid.UUID
    institution_name: str

    class Config:
        from_attributes = True
