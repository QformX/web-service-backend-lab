from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    bio: str | None = None
    image_url: str | None = None

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "secret123",
                "bio": "About me",
                "image_url": "https://example.com/avatar.png"
            }
        ]
    })


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "email": "user@example.com",
                "password": "secret123"
            }
        ]
    })


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None
    bio: str | None = None
    image_url: str | None = None

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "email": "new@example.com",
                "username": "john",
                "password": "newpass",
                "bio": "New bio",
                "image_url": "https://example.com/new.png"
            }
        ]
    })


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    bio: str | None = None
    image_url: str | None = None
    subscription_key: str | None = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "examples": [
            {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "bio": "About me",
                "image_url": "https://example.com/avatar.png",
                "subscription_key": "secret-key"
            }
        ]
    })


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        ]
    })


class SubscriptionKeyUpdate(BaseModel):
    subscription_key: str = Field(min_length=1, max_length=512)

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {"subscription_key": "secret-key-from-push-service"}
        ]
    })


class SubscribeRequest(BaseModel):
    target_user_id: int = Field(gt=0)

    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {"target_user_id": 2}
        ]
    })


