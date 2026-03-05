from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr


class ChatRequest(BaseModel):
    message: str
    session_messages: list[dict] = []


class AuthResponse(BaseModel):
    token: str
    status: str
    messages_remaining: int | None = None


class UsageResponse(BaseModel):
    messages_used: int
    messages_remaining: int
    limit: int
