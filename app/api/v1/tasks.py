from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import User, Task
from app.schemas import TaskRead, TaskCreate, TaskUpdate

task_router = APIRouter(prefix="/tasks", tags=["tasks"])


@task_router.get("/", response_model=list[TaskRead])
async def get_tasks(
        project_id: int | None = None,
        only_open: bool = True,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    query = select(Task).where(Task.assigned_to_id == current_user.id)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if only_open:
        query = query.where(Task.status.is_(False))
    result = await db.execute(query)
    tasks = result.scalars().all()
    return [TaskRead.model_validate(t) for t in tasks]


@task_router.post("/", response_model=TaskRead)
async def create_task(
        task_in: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> TaskRead:
    data = task_in.model_dump()
    if data.get("assigned_to_id") is None:
        data["assigned_to_id"] = current_user.id
    new_task = Task(**data)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return TaskRead.model_validate(new_task)


@task_router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> TaskRead:
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.assigned_to_id == current_user.id)
    )
    task = result.scalars().first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    data = task_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return TaskRead.model_validate(task)
