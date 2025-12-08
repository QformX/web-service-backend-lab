from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select

from src.api.v1.users.schemas import (
    SubscribeRequest,
    SubscriptionKeyUpdate,
    TokenOut,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)
from src.infrastructure.db.deps import get_db
from src.infrastructure.db.models import Subscription, User
from src.common.security.passwords import hash_password, verify_password
from src.common.security.jwt import create_access_token
from src.common.security.deps import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    result = await db.execute(select(User).where((User.email == payload.email) | (User.username == payload.username)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered")
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        bio=payload.bio,
        image_url=payload.image_url,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenOut)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenOut:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    # Add user ID and username to token payload so other services can identify the user
    token = create_access_token(subject=user.email, extra={"id": user.id, "username": user.username})
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.put("/me", response_model=UserOut)
async def update_current_user(payload: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserOut:
    if payload.email and payload.email != current_user.email:
        result = await db.execute(select(User).where(User.email == payload.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        current_user.email = payload.email
    if payload.username and payload.username != current_user.username:
        result = await db.execute(select(User).where(User.username == payload.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use")
        current_user.username = payload.username
    if payload.password:
        current_user.password_hash = hash_password(payload.password)
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.image_url is not None:
        current_user.image_url = payload.image_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.put("/me/subscription-key", response_model=UserOut)
async def update_subscription_key(
    payload: SubscriptionKeyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    sanitized = payload.subscription_key.strip()
    if not sanitized:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Subscription key cannot be empty")
    current_user.subscription_key = sanitized
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def subscribe_to_user(
    payload: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot subscribe to yourself")

    target_user = await db.get(User, payload.target_user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    result = await db.execute(
        select(Subscription).where(
            Subscription.subscriber_id == current_user.id,
            Subscription.target_user_id == payload.target_user_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    subscription = Subscription(subscriber_id=current_user.id, target_user_id=payload.target_user_id)
    db.add(subscription)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


