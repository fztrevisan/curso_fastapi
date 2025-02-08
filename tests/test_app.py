from http import HTTPStatus

from fastapi.testclient import TestClient


def test_root_deve_retornar_ok_e_ola_mundo(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_formatted_retorna_ok_e_ola_mundo_em_html(client: TestClient):
    response = client.get('/formatted')

    assert response.status_code == HTTPStatus.OK
    assert 'Olá mundo' in response.text


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


def test_read_users(client: TestClient):
    # Bad practice because it depends on the previous test...
    # It remains like this for didactic purposes
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'testusername',
                'email': 'test@email.com',
            }
        ]
    }


def test_update_user(client: TestClient):
    response = client.put(
        url='/users/1',
        json={
            'id': 1,
            'username': 'testusername2',
            'email': 'test@email.com',
            'password': '1234',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'testusername2',
        'email': 'test@email.com',
    }


def test_delete_user(client: TestClient):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User testusername2 deleted'}

# TODO Escrever testes para os 404 nos endpoints de update e delete