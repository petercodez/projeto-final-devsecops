from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from app.models import Task, TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class TaskAlreadyCompletedError(Exception):
    pass


class InvalidDueDateError(Exception):
    pass


class TaskService:
    """Armazenamento em memória com as regras de negócio das tarefas."""

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    @staticmethod
    def _validate_due_date(due_date: Optional[date]) -> None:
        if due_date is not None and due_date < date.today():
            raise InvalidDueDateError("due_date cannot be in the past")

    def create(self, data: TaskCreate) -> Task:
        self._validate_due_date(data.due_date)
        task = Task(
            id=self._next_id,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            completed=False,
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_tasks(self, completed: Optional[bool] = None) -> List[Task]:
        tasks = list(self._tasks.values())
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def get(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"task {task_id} not found")
        return task

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get(task_id)
        if task.completed:
            raise TaskAlreadyCompletedError(f"task {task_id} is already completed")
        self._validate_due_date(data.due_date)
        updated = task.model_copy(
            update={
                "title": data.title,
                "description": data.description,
                "due_date": data.due_date,
            }
        )
        self._tasks[task_id] = updated
        return updated

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if task.completed:
            raise TaskAlreadyCompletedError(f"task {task_id} is already completed")
        completed = task.model_copy(update={"completed": True})
        self._tasks[task_id] = completed
        return completed

    def delete(self, task_id: int) -> None:
        self.get(task_id)
        del self._tasks[task_id]