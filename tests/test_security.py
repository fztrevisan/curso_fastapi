from http import HTTPStatus

from fastapi.testclient import TestClient
from jwt import decode

from fast_zero.schemas import UserSchema
from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    result = decode(
        token,
        key=SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_get_token(client: TestClient, user: UserSchema):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


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
    """ Test token generated without and email ('sub' key)
    """
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
    """ Test token generated with an email that doesnt exist
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
