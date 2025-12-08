from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=1000)
    status: bool = False
    priority: int = Field(1, ge=1, le=5)
    project_id: int
    assigned_to_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=1000)
    status: bool | None = None
    priority: int | None = Field(None, ge=1, le=5)
    assigned_to_id: int | None = None
