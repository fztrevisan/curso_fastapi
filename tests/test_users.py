from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.schemas import UserPublic


def test_create_user(client: TestClient):
    response = client.post(
        url='/users/',
        json={
            'username': 'testusername',
            'password': 'testpassword',
            'email': 'test@email.com',
        },
    )
    # Validate UserPublic
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'testusername',
        'email': 'test@email.com',
    }


def test_create_user_error_username_exists(client: TestClient, user):
    response = client.post(
        url='/users/',
        json={
            'username': user.username,
            'password': 'testpwd',
            'email': 'testemail@email.com',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Username already exists',
    }


def test_create_user_error_email_exists(client: TestClient, user):
    response = client.post(
        url='/users/',
        json={
            'username': 'testusername',
            'password': 'testpwd',
            'email': user.email,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Email already exists',
    }


def test_read_user(client: TestClient, user):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_read_user_not_found(client: TestClient):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users(client: TestClient):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client: TestClient, user, other_user):
    user_schema = UserPublic.model_validate(user).model_dump()
    other_user_schema = UserPublic.model_validate(other_user).model_dump()
    
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema, other_user_schema]}


def test_update_user(client: TestClient, user, token):
    response = client.put(
        url=f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'testusername2',
            'email': 'test@email.com',
            'password': '1234',
        },
    )

    assert response.json() == {
        'id': user.id,
        'username': 'testusername2',
        'email': 'test@email.com',
    }


def test_update_user_with_wrong_user(client: TestClient, other_user, token):
    response = client.put(
        url=f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@email.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client: TestClient, user, token):
    response = client.delete(
        url=f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'message': 'User deleted'}


def test_delete_user_with_wrong_user(client: TestClient, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
