from http import HTTPStatus
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from fast_zero.routers import auth, todo, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)


@app.get('/', status_code=HTTPStatus.OK, response_class=FileResponse)
def read_root():
    html_path = Path(__file__).parent / 'static' / 'index.html'
    return FileResponse(html_path, media_type='text/html')
