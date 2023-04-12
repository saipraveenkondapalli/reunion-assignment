import json
import pytest

from project.app import app
from project.models import User


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def login(client, id):
    """
    Login user with given id
    :param client:
    :param id:
    :return: TOKEN
    """
    USER = User.objects(id=id).first()
    response = client.post('/api/authenticate',
                           data=json.dumps({'email': USER.email, 'password': USER.password}),
                           content_type='application/json')

    assert response.status_code == 200
    token = response.json['token']
    return token


def test_like_postive(client):
    """
    Authorized user try to like a post
    EXample:
    USER with ID 1 try to like a post with ID 2
    :param client:
    :return:
    """

    token = login(client, 1)
    response = client.post('/api/like/2',
                           headers={'Authorization': token},
                           content_type='application/json')
    # Liked post or already liked
    assert response.status_code == 200
    assert 'message' in response.json


def test_like_negative(client):
    """
    Authorized user try to like a post that does not exist Example USER with ID 1 try to like a post with ID 100
    :param client:
    :return:
    """

    token = login(client, 1)
    response = client.post('/api/like/100',
                           headers={'Authorization': token},
                           content_type='application/json')
    # 404 - Post not found
    assert response.status_code == 404
    assert 'error' in response.json


def test_unlike_positive(client):
    """
    Authorized user try to unlike a post
    EXample:
    USER with ID 1 try to unlike a post with ID 2
    :param client:
    :return:
    """

    token = login(client, 1)
    response = client.post('/api/unlike/3',
                           headers={'Authorization': token},
                           content_type='application/json')
    # 200 - Unliked post or already unliked
    assert response.status_code == 200
    assert 'message' in response.json


def test_unlike_negative(client):
    """
    Authorized user try to unlike a post that does not exist
    Example:
    USER with ID 1 try to unlike a post with ID 100
    :param client:
    :return:
    """
    token = login(client, 1)
    response = client.post('/api/unlike/100',
                           headers={'Authorization': token},
                           content_type='application/json')
    # 404 - Post not found
    assert response.status_code == 404
    assert 'error' in response.json


def test_comment_positive(client):
    """
    Authorized user try to comment a post
    Example:
    USER with ID 1 try to comment a post with ID 2
    :param client:
    :return:
    """
    token = login(client, 1)
    response = client.post('/api/comment/2',
                           headers={'Authorization': token},
                           data=json.dumps({'comment': 'Test comment'}),
                           content_type='application/json')
    # 201 - Comment added
    assert response.status_code == 200
    assert 'Comment-ID' in response.json


def test_comment_negative(client):
    """
    Authorized user try to comment a post that does not exist
    :param client:
    :return:
    """
    token = login(client, 1)
    response = client.post('/api/comment/1000',
                           headers={'Authorization': token},
                           data=json.dumps({'comment': 'Test comment'}),
                           content_type='application/json')
    # 404 - Post not found
    assert response.status_code == 404
