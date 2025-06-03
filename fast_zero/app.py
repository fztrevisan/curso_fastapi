from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.routers import auth, todo, users
from fast_zero.schemas import Message

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)


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
