from http import HTTPStatus

from fastapi.testclient import TestClient
from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    result = decode(
        token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client: TestClient):
    token = 'invalid_token'
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate the provided credentials'
    }


def test_get_current_user_email_not_found(client: TestClient):
    """Test token generated without and email ('sub' key)"""
    data = {'no-sub': 'no-email'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate the provided credentials'
    }


def test_get_current_user_doesnt_exist(client: TestClient):
    """Test token generated with an email that doesnt exist
    in the database
    """
    data = {'sub': 'non-existent@email.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate the provided credentials'
    }
