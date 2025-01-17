from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


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
