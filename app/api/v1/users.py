from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserRead
from app.auth.password import hashed_password

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]


@user_router.post("/")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    hashed_pass = hashed_password(user_in.password)
    new_user = User(username=user_in.username, email=user_in.email, password=hashed_pass)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserRead.model_validate(new_user)


@user_router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user
