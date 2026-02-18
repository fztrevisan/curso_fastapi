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


# Test oauth endpoints
def test_list_todos_rate_limit(client_with_rate_limit, token, rate_limit):
    # A fixture token já faz 1 chamada no endpoint de auth
    # O loop abaixo deve fazer só mais 4
    # FIXME teste dando erro
    for _ in range(rate_limit - 2):
        response = client_with_rate_limit.get(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json()['todos'] == []

    response = client_with_rate_limit.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert response.json() == {
        'error': f'Rate limit exceeded: {rate_limit} per 1 minute'
    }
