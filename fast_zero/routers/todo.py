from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoState,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=["To-Do's"])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
def create_todo(
    todo: TodoSchema,
    session: T_Session,
    user: T_CurrentUser,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(
    session: T_Session,
    user: T_CurrentUser,
    title: str | None = None,
    description: str | None = None,
    state: TodoState | None = None,
    offset: int = 0,
    limit: int = 100,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.icontains(title))

    if description:
        query = query.filter(Todo.description.icontains(description))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()

    return {'todos': todos}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(
    todo_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_todo = session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    session.delete(db_todo)
    session.commit()

    return {'message': 'Task deleted successfully'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def update_todo(
    todo_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
    todo: TodoUpdate,
):
    db_todo = session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
