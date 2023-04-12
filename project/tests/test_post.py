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
    Get a post with given id
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


def test_get_post_negative(client):
    """
    Try to get a post that does not exist and look for error code 404 and check error message in response
    :param client:
    :return:
    """
    post_id = 100
    response = client.get(f'/api/posts/{post_id}')
    assert response.status_code == 404
    assert 'error' in response.json


def test_get_all_posts(client):
    """
    Get all posts
    """
    response = client.get('/api/all_posts')
    assert response.status_code == 200
    assert len(response.json) > 0


def test_post_create(client):
    """
    Create a new post after login with valid credentials
    Here we are creating 3 posts with title and description
    we get the highest id from the database and add 1 to it for the title and description
    """

    token = login(client, 1)
    post_highest_id = Post.objects().order_by('-id').first()
    if not post_highest_id:
        post_highest_id = 1
    else:
        post_highest_id = post_highest_id.id + 1

    response = client.post('/api/posts',
                           data=json.dumps({'title': f'Sample Title for post created by Pytest {post_highest_id}',
                                            'description': f'Sample Description for post {post_highest_id}'}),
                           headers={'Authorization': token},
                           content_type='application/json')
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'Title' in response.json
    assert 'Description' in response.json
    assert 'Created Time(UTC)' in response.json


def test_post_create_negative(client):
    """
    Try to create a post with missing title by authorized user
    """
    token = login(client, 1)
    response = client.post('/api/posts',
                           data=json.dumps({'description': 'Sample Description for post 1'}),
                           headers={'Authorization': token},
                           content_type='application/json')

    assert response.status_code == 400
    assert 'error' in response.json


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
    # 404 - Post does not exist or already deleted

    assert response.status_code == 200 or response.status_code == 404


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
