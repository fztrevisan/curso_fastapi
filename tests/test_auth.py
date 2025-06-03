from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from fast_zero.schemas import UserSchema


def test_get_token(client: TestClient, user: UserSchema):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'token_type' in token
    assert 'access_token' in token


def test_get_token_expired_after_time(client: TestClient, user: UserSchema):
    with freeze_time('2021-01-14 17:00:00'):
        # Gerar o token às 17:00
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2021-01-14 17:31:00'):
        # Usar o token 17:35
        response = client.put(
            url=f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wronguser',
                'email': 'wrong@wrong.com',
                'password': 'wrongpassword',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Expired token'}


def test_get_token_wrong_email(client: TestClient):
    response = client.post(
        '/auth/token',
        data={
            'username': 'non_existent@mail.com',
            'password': 'non-existent-password',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_wrong_password(client: TestClient, user: UserSchema):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrongpassword'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client: TestClient, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_refresh_token_expired_after_time(
    client: TestClient, user: UserSchema
):
    with freeze_time('2021-01-14 17:00:00'):
        # Gerar o token às 17:00
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2021-01-14 17:31:00'):
        # Usar o token 17:35
        response = client.post(
            url='/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Expired token'}
