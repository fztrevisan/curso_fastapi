from http import HTTPStatus
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from fast_zero.routers import auth, todo, users


limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])

app = FastAPI()
# adds rate limit to all routes in the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)


@app.get('/', status_code=HTTPStatus.OK, response_class=FileResponse)
def read_root():
    html_path = Path(__file__).parent / 'static' / 'index.html'
    return FileResponse(html_path, media_type='text/html')
