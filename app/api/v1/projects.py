from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import User, Project
from app.schemas import ProjectCreate, ProjectRead

project_router = APIRouter(prefix="/projects", tags=["projects"])


@project_router.get("/")
async def get_projects(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id)
    )
    projects = result.scalars().all()
    return [ProjectRead.model_validate(p) for p in projects]


@project_router.post("/")
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)) -> ProjectRead:
    new_project = Project(
        **project_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return ProjectRead.model_validate(new_project)
