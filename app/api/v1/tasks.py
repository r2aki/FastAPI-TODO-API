from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import User, Task, Project
from app.schemas import TaskRead, TaskCreate, TaskUpdate

task_router = APIRouter(prefix="/tasks", tags=["tasks"])


@task_router.get("/", response_model=list[TaskRead])
async def get_tasks(
        project_id: int | None = None,
        status: bool | None = None,
        min_priority: int | None = None,
        max_priority: int | None = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    query = select(Task).where(Task.assigned_to_id == current_user.id)

    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if status is not None:
        query = query.where(Task.status.is_(status))
    if min_priority is not None:
        query = query.where(Task.priority >= min_priority)
    if max_priority is not None:
        query = query.where(Task.priority <= max_priority)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    tasks = result.scalars().all()
    return [TaskRead.model_validate(t) for t in tasks]


@task_router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
        task_in: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> TaskRead:
    data = task_in.model_dump()

    result = await db.execute(
        select(Project).where(
            Project.id == data["project_id"],
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalars().first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

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


@task_router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    query = select(Task).where(Task.id == task_id, Task.assigned_to_id == current_user.id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@task_router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    query = select(Task).where(Task.id == task_id, Task.assigned_to_id == current_user.id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
