from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Task, User
from schemas import TaskCreate, TaskRead, TaskUpdate, TaskStatus
from dependencies import get_current_user

router = APIRouter()


def get_owned_task_or_404(task_id: int, db: Session, current_user: User) -> Task:
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == current_user.id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.post("", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        owner_id=current_user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    status_filter: TaskStatus | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # only ever query tasks belonging to the logged-in user - this is
    # the actual server-side enforcement of "you only see your own data"
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter)

    return query.offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_task_or_404(task_id, db, current_user)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_owned_task_or_404(task_id, db, current_user)

    # only overwrite fields the caller actually sent (exclude_unset=True),
    # so a partial update doesn't accidentally wipe out other fields
    updates = task_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_owned_task_or_404(task_id, db, current_user)
    db.delete(task)
    db.commit()
    return None
