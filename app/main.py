from fastapi import FastAPI, Depends
from sqlalchemy import text

from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.user import user_router
from app.auth.router import auth_router

app = FastAPI(title="TODO")
app.include_router(user_router)
app.include_router(auth_router)


@app.get("/")
async def index():
    return {"status": "ok"}


@app.get("/db-check")
async def get_db_test(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text('SELECT 1'))
    return {"status": "ok"} if result.scalar() == 1 else {"status": "error"}
