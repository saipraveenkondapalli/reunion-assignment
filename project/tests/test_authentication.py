from project.app import app
from project.models import User

import json
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def login(client, email, password):
    """
    Login user with given id
    :param client:
    :param id:
    :return: TOKEN
    """
    USER = {
        'email': email,
        'password': password
    }
    response = client.post('/api/authenticate',
                           data=json.dumps({'email': USER['email'], 'password': USER['password']}),
                           content_type='application/json')

    assert response.status_code == 200
    token = response.json['token']

    return token


def test_authentication_positive(client):
    """
    Test authentication with valid credentials
    Database has 5 users with id 1 to 5
    :param client:
    :return: token
    """
    USER = User.objects(id=1).first()

    response = client.post('/api/authenticate',
                           data=json.dumps({'email': USER.email, 'password': USER.password}),
                           content_type='application/json')
    assert response.status_code == 200
    assert 'token' in response.json


def test_authentication_negative(client):
    """
    Test authentication with invalid credentials
    :param client:
    :return:
    """
    response = client.post('/api/authenticate',
                           data=json.dumps({'email': 'john@example.com', 'password': 'password'}),
                           content_type='application/json')
    assert response.status_code == 401


def test_authentication_missing_credentials(client):
    """
    Test authentication with missing credentials
    :param client:
    :return:
    """
    response = client.post('/api/authenticate',
                           content_type='application/json')

    assert response.status_code == 400


def test_user_profile_positive(client):
    """
    Test user profile, positive case i.e authenticated user
    Example:
    email = john@example.com
    password = password123
    :param client:
    :return:
    """
    USER = {
        'email': 'john@example.com',
        'password': 'password123'
    }

    token = login(client, USER['email'], USER['password'])

    response = client.get(f'/api/user',
                          headers={'Authorization': token},
                          content_type='application/json')

    assert response.status_code == 200


def test_user_profile_negative(client):
    """
    Test user profile, negative case i.e unauthorized user, no token
    :param client:
    :return:
    """

    response = client.get(f'/api/user',
                          content_type='application/json')
    # Token is missing so invalid credentials
    assert response.status_code == 400
