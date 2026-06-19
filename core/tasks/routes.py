from typing import List, Annotated

from fastapi import APIRouter, Path, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.auth.jwt_auth import get_jwt_token_authenticated_user
from core.database import get_db
from core.tasks.models import TaskModel
from core.tasks.schemas import *
from core.users.models import UserModel

router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks_list(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[UserModel, Depends(get_jwt_token_authenticated_user)],
        completed: bool = Query(None, description="filter tasks based on being completed or not"),
        limit: int = Query(10, gt=0, le=50, description="limiting the number of items to retrieve"),
        offset: int = Query(0, ge=0, description="use for paginating based on passed items"),
):
    query = db.query(TaskModel).filter_by(user_id=user.id)
    if completed is not None:
        query = query.filter_by(is_completed=completed)

    return query.limit(limit).offset(offset).all()


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_task_detail(
        user: Annotated[UserModel, Depends(get_jwt_token_authenticated_user)],
        task_id: int = Path(..., gt=0),
        db: Session = Depends(get_db)
):
    task_obj = db.query(TaskModel).filter_by(id=task_id, user_id=user.id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_task(
        user: Annotated[UserModel, Depends(get_jwt_token_authenticated_user)],
        request: TaskCreateSchema, db: Session = Depends(get_db)
):
    data = request.model_dump()
    data.update({'user_id': user.id})
    task_obj = TaskModel(**data)
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(
        user: Annotated[UserModel, Depends(get_jwt_token_authenticated_user)],
        request: TaskUpdateSchema, task_id: int = Path(..., gt=0),
        db: Session = Depends(get_db)
):
    task_obj = db.query(TaskModel).filter_by(id=task_id, user_id=user.id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields using setattr
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_obj, field, value)

    db.commit()  # Commit the changes to the database
    db.refresh(task_obj)  # Refresh the task object to reflect the updated data

    return task_obj  # Return the updated task object


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
        user: Annotated[UserModel, Depends(get_jwt_token_authenticated_user)],
        task_id: int = Path(..., gt=0),
        db: Session = Depends(get_db)
):
    task_obj = db.query(TaskModel).filter_by(id=task_id, user_id=user.id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task_obj)
    db.commit()
