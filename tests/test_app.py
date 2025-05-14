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


def test_login_for_access_token_bad_request(client: TestClient, session):
    data = {'username': 'non-existent@email.com', 'password': '123456'}
    response = client.post('/auth/token', data=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}
