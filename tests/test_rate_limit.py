from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.schemas import UserPublic
from tests.conftest import UserFactory


# Test open endpoints
def test_read_users_rate_limit(
    client_with_rate_limit: TestClient, rate_limit: int
):
    for _ in range(rate_limit):
        response = client_with_rate_limit.get('/users/')
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'users': []}

    response = client_with_rate_limit.get('/users/')
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert response.json() == {
        'error': f'Rate limit exceeded: {rate_limit} per 1 minute'
    }


def test_create_user_rate_limit(
    client_with_rate_limit: TestClient, rate_limit: int
):
    users = UserFactory.create_batch(rate_limit)

    for i, user in enumerate(users, start=1):
        user.id = i
        user_public = UserPublic.model_validate(user).model_dump()
        response = client_with_rate_limit.post(
            url='/users/',
            json={
                'username': user.username,
                'password': user.password,
                'email': user.email,
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == user_public

    response = client_with_rate_limit.post(
        url='/users/',
        json={
            'username': 'anotherusername',
            'password': 'anotherpassword',
            'email': 'another@email.com',
        },
    )
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert response.json() == {
        'error': f'Rate limit exceeded: {rate_limit} per 1 minute'
    }


# Test protected endpoints
def test_list_todos_rate_limit(
    client_with_rate_limit: TestClient,
    token_with_rate_limit: str,
    rate_limit: int,
):
    for _ in range(rate_limit):
        response = client_with_rate_limit.get(
            '/todos/',
            headers={'Authorization': f'Bearer {token_with_rate_limit}'},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['todos'] == []

    response = client_with_rate_limit.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token_with_rate_limit}'},
    )
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert response.json() == {
        'error': f'Rate limit exceeded: {rate_limit} per 1 minute'
    }


# Test calling multiple protected endpoints
def test_call_multiple_protected_endpoints(
    client_with_rate_limit: TestClient,
    token_with_rate_limit: str,
    rate_limit: int,
):
    """Cria 2 ToDos e faz 3 GETs dentro do limite.
    Depois faz 1 GET fora do limite para causar erro.
    """
    for i in range(2):
        # Create todo
        response = client_with_rate_limit.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token_with_rate_limit}'},
            json={
                'title': f'Test todo {i}',
                'description': f'Test todo description {i}',
                'state': 'draft',
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        # List todos
        response = client_with_rate_limit.get(
            '/todos/',
            headers={'Authorization': f'Bearer {token_with_rate_limit}'},
        )
        assert response.status_code == HTTPStatus.OK
    # 5o request (ainda dentro do limite)
    response = client_with_rate_limit.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token_with_rate_limit}'},
    )
    assert response.status_code == HTTPStatus.OK
    # 6o request (fora do limite)
    response = client_with_rate_limit.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token_with_rate_limit}'},
    )
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert response.json() == {
        'error': f'Rate limit exceeded: {rate_limit} per 1 minute'
    }
