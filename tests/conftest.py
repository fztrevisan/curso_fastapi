import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        """This function will be called instead of the original `get_session()`

        Calls the session fixture to get the sqlite memory session"""
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        url='sqlite:///:memory:',
        # avoid "sqlite3.ProgrammingError: SQLite objects created in a thread
        # can only be used in that same thread."
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    pwd = 'testando123'
    user = User(
        username='Teste',
        email='teste@teste.com',
        password=get_password_hash(pwd),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd  # Monkey patch
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']
