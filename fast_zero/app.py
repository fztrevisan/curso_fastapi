from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


# response_class informs FastAPI that the response will be diffent from JSON
@app.get('/formatted', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_formatted():
    return """
        <html lang="pt-br">
        <head>
            <title>Meu olá mundo</title>
        </head>
        <body>
            <h1>Olá mundo</h1>
        </body>
        </html>
    """


# response_model informs FastAPI that the response has to follow the schema
# defined in the parameter
@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already registered',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already registered',
            )

    db_user = User(
        username=user.username, email=user.email, password=user.password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(
    limit: int = 10,
    skip: int = 0,
    session: Session = Depends(get_session),
):
    users = session.scalars(select(User).limit(limit).offset(skip)).all()
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(User).where(User.id == user_id))
    # session.get(User, user_id) # Também funciona!!
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    db_user = session.get(User, user_id)  # Também funciona!!
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(db_user)
    session.commit()
    return {'message': 'User deleted'}


# @app.get('/users/{user_id}', response_model=UserPublic)
# def read_user(user_id: int):
#     if user_id > len(database) or user_id < 1:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail='User not found'
#         )
#     return database[user_id - 1]
