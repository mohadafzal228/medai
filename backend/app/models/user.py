from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: str

class UserLogin(UserBase):
    password: str

class UserInDB(UserBase):
    full_name: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    otp: Optional[str] = None
    otp_expiry: Optional[datetime] = None
    last_otp_request: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(BaseModel):
    user_email: str
    messages: List[ChatMessage] = []

class ChatRequest(BaseModel):
    message: str
