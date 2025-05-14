from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.schemas import UserSchema


def test_get_token(client: TestClient, user: UserSchema):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
