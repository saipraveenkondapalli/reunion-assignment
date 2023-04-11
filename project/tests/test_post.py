from project.app import app
from project.models import User, Post
import json
import pytest


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


def test_get_post(client):
    """
    Get all posts
    :param client:
    :return:
    """
    post_id = 3
    response = client.get(f'/api/posts/{post_id}')
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'title' in response.json
    assert 'description' in response.json
    assert 'likes' in response.json
    assert 'comments' in response.json


def test_post_create(client):
    """
    Create a new post after login with valid credentials
    :param client:
    :return:
    """

    token = login(client, 1)
    post_highest_id = Post.objects().order_by('-id').first()
    if not post_highest_id:
        post_highest_id = 1
    else:
        post_highest_id = post_highest_id.id + 1

    # create 3 new posts
    for i in range(post_highest_id, post_highest_id + 4):
        response = client.post('/api/posts',
                               data=json.dumps({'title': f'Sample Post {i}',
                                                'description': f'Sample Description for post {i}'}),
                               headers={'Authorization': token},
                               content_type='application/json')

        assert response.status_code == 201


def test_delete_post_positive(client):
    """
    Delete a post after login with valid credentials
    Example:
    USER with ID 1 created a post with ID 1, now  USER with id 1 is trying to delete the post with ID 1
    :param client:
    :return:
    """

    token = login(client, 1)
    response = client.delete('/api/posts/1',
                             headers={'Authorization': token},
                             content_type='application/json')

    # 200 - Deleted successfully
    # 400 - Post does not exist or already deleted

    assert response.status_code == 200 or response.status_code == 401


def test_delete_post_negative(client):
    """
    Try to delete a post that does not exist, after login with valid credentials
    :param client:
    :return:
    """

    token = login(client, 1)
    response = client.delete('/api/posts/100',
                             headers={'Authorization': token},
                             content_type='application/json')

    assert response.status_code == 401


def test_delete_post_unauthorized(client):
    """
    Try to delete a post created by another user
    Example : USER with ID 1 created a post with ID 2, now  USER with id 2 is trying to delete the post with ID 2fprin
    :param client:
    :return:
    """
    token = login(client, 2)
    response = client.delete('/api/posts/2',
                             headers={'Authorization': token},
                             content_type='application/json')

    assert response.status_code == 401
