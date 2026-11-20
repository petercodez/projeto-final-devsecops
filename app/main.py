import logging
from typing import List, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app import config
from app.models import Task, TaskCreate, TaskUpdate
from app.service import (
    InvalidDueDateError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
    TaskService,
)

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("todo-api")
logger.info("starting todo-api version=%s env=%s", config.APP_VERSION, config.APP_ENV)

app = FastAPI(
    title="To-Do API",
    description="API de gerenciamento de tarefas - Projeto Final Integração DevOps",
    version=config.APP_VERSION,
)

_service = TaskService()


def get_service() -> TaskService:
    return _service


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    logger.warning("not found: %s", exc)
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TaskAlreadyCompletedError)
async def task_completed_handler(request: Request, exc: TaskAlreadyCompletedError):
    logger.warning("conflict: %s", exc)
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidDueDateError)
async def invalid_due_date_handler(request: Request, exc: InvalidDueDateError):
    logger.warning("invalid due date: %s", exc)
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health", tags=["monitoring"])
def health():
    return {"status": "ok", "version": config.APP_VERSION, "environment": config.APP_ENV}


@app.post("/tasks", response_model=Task, status_code=201, tags=["tasks"])
def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    task = service.create(data)
    logger.info("task created id=%s", task.id)
    return task


@app.get("/tasks", response_model=List[Task], tags=["tasks"])
def list_tasks(
    completed: Optional[bool] = None, service: TaskService = Depends(get_service)
):
    return service.list_tasks(completed)


@app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    return service.get(task_id)


@app.put("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def update_task(
    task_id: int, data: TaskUpdate, service: TaskService = Depends(get_service)
):
    task = service.update(task_id, data)
    logger.info("task updated id=%s", task_id)
    return task


@app.patch("/tasks/{task_id}/complete", response_model=Task, tags=["tasks"])
def complete_task(task_id: int, service: TaskService = Depends(get_service)):
    task = service.complete(task_id)
    logger.info("task completed id=%s", task_id)
    return task


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"])
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    service.delete(task_id)
    logger.info("task deleted id=%s", task_id)