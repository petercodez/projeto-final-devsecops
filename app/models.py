from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value


class TaskUpdate(TaskCreate):
    """PUT substitui os campos editáveis da tarefa."""


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: bool = False
    created_at: datetime