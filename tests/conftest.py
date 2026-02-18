from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

# from sqlalchemy.pool import StaticPool
from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User, table_registry
from fast_zero.security import get_password_hash

# from fast_zero.settings import Settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text', max_nb_chars=20)
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


# FONTES:
# 1. https://stackoverflow.com/questions/29116718/how-to-mocking-created-time-in-sqlalchemy
# 2. https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.MapperEvents
@contextmanager
def _mock_db_time(*, model, fake_time=datetime(2024, 1, 1)):
    def set_fake_time(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = fake_time
        if hasattr(target, 'updated_at'):
            target.updated_at = fake_time

    event.listen(model, 'before_insert', set_fake_time)
    yield fake_time
    event.remove(model, 'before_insert', set_fake_time)


@pytest.fixture
def client(session):
    """Client with rate limiting disabled and local db"""

    def get_session_override():
        """This function will be called instead of the original `get_session()`

        Calls the session fixture to get the local postgres memory session"""
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        app.state.limiter.enabled = False
        yield client

    app.dependency_overrides.clear()
    app.state.limiter.enabled = True


@pytest.fixture
def client_with_rate_limit(session):
    """Client with rate limiting enabled for testing rate limit behavior."""

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        # Set rate limit
        app.state.limiter.enabled = True
        app.state.limiter.reset()
        yield client

    app.dependency_overrides.clear()
    app.state.limiter.reset()


@pytest.fixture
def rate_limit() -> int:
    return 5


# Fixture usada antes do postgres, com SQLite em memória.
# Deixei aqui para referência, mas não é mais usada.
# Para voltar a usar reativar o import do StaticPool
# @pytest.fixture
# def session():
#     engine = create_engine(
#         url='sqlite:///:memory:',
#         # avoid "sqlite3.ProgrammingError: SQLite objects created in a thread
#         # can only be used in that same thread."
#         connect_args={'check_same_thread': False},
#         poolclass=StaticPool,
#     )
#     table_registry.metadata.create_all(engine)

#     with Session(engine) as session:
#         yield session

#     table_registry.metadata.drop_all(engine)


# Usa o banco certo mas depende do postgres estar rodando.
# Deleta as tabelas toda vez que rodar os testes
# Voltar o import Settings para usar
# @pytest.fixture
# def session():
#     engine = create_engine(Settings().DATABASE_URL)
#     table_registry.metadata.create_all(engine)

#     with Session(engine) as session:
#         yield session

#     table_registry.metadata.drop_all(engine)


# scope=session para criar o banco uma vez por sessão de teste,
# e não para cada teste individual
@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    pwd = 'testando123'
    user = UserFactory(
        password=get_password_hash(pwd),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd  # Monkey patch
    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def token_with_rate_limit(client_with_rate_limit, user):
    response = client_with_rate_limit.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def mock_db_time():
    """
    Fixture to mock the database time for created_at and updated_at fields
    """
    return _mock_db_time
