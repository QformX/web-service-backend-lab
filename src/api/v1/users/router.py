from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.api.v1.users.schemas import UserCreate, UserLogin, UserOut, UserUpdate, TokenOut
from src.infrastructure.db.deps import get_db
from src.infrastructure.db.models import User
from src.common.security.passwords import hash_password, verify_password
from src.common.security.jwt import create_access_token
from src.common.security.deps import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    if db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered")
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        bio=payload.bio,
        image_url=payload.image_url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenOut)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.put("/me", response_model=UserOut)
def update_current_user(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserOut:
    if payload.email and payload.email != current_user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        current_user.email = payload.email
    if payload.username and payload.username != current_user.username:
        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use")
        current_user.username = payload.username
    if payload.password:
        current_user.password_hash = hash_password(payload.password)
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.image_url is not None:
        current_user.image_url = payload.image_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


