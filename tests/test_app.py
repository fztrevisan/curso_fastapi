from http import HTTPStatus

from fastapi.testclient import TestClient


def test_root_deve_retornar_ok_e_landing_page(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert 'text/html' in response.headers['content-type']
    assert 'Fast Zero API' in response.text
    assert 'Fernando Trevisan' in response.text


def test_login_for_access_token_bad_request(client: TestClient, session):
    data = {'username': 'non-existent@email.com', 'password': '123456'}
    response = client.post('/auth/token', data=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}
