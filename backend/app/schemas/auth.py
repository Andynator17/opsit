"""Authentication schemas"""
from pydantic import BaseModel
from app.schemas.user import UserResponse


class Token(BaseModel):
    """JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Token with user info"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
