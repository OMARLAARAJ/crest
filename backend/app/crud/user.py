from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == _normalize_email(email)))


def get_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        email=_normalize_email(payload.email),
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    user = get_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_profile(db: Session, user: User, payload: UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current: str, new: str) -> bool:
    if not verify_password(current, user.hashed_password):
        return False
    user.hashed_password = hash_password(new)
    db.add(user)
    db.commit()
    db.refresh(user)
    return True
