from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

database = []


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
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user_with_id


@app.get('/users/', response_model=UserList)
def read_users():
    return {'users': database}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )

    user_with_id = database.pop(user_id - 1)
    return {'message': f'User {user_with_id.username} deleted'}

#TODO Criar um endpoint GET para buscar um usuário pelo ID `users/{user_id}` e fazer testes!!
#TODO Quizz aula 03
#TODO Assistir as lives de SQLAlchemy e Migrações