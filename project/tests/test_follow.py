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

    if response.status_code == 200:
        token = response.json['token']
        return token

    return None


def test_follow(client):
    """
    Test follow user, positive case i.e authenticated user follow another user
    :param client:
    :return:
    """
    USER = User.objects(id=1).first()
    USER_TO_FOLLOW_IDs = [2, 3, 4, 5]

    token = login(client, 1)

    for id in USER_TO_FOLLOW_IDs:
        response = client.post(f'/api/follow/{id}',
                           headers={'Authorization': token},
                           content_type='application/json')
        # 200 - Followed successfully
        # 202 - Already following
        assert response.status_code == 200 or response.status_code == 202


def test_user_already_following(client):
    """
    Test follow user, negative case i.e authenticated user already following another user
    :param client:
    :return:
    """
    USER = User.objects(id=1).first()
    USER_TO_FOLLOW = User.objects(id=5).first()
    token = login(client, 1)

    response = client.post(f'/api/follow/{USER_TO_FOLLOW.id}',
                           headers={'Authorization': token},
                           content_type='application/json')
    USER.reload()
    USER_TO_FOLLOW.reload()
    assert response.status_code == 202
    assert response.json['message'] == 'You already follow this user'


def test_user_to_follow_not_exists(client):
    """
    Test follow user, negative case i.e authenticated user follow non existing user
    :param client:
    :return:
    """
    USER = User.objects(id=1).first()
    USER_TO_FOLLOW_ID = 6  # non existing user
    token = login(client, 1)

    response = client.post(f'/api/follow/{USER_TO_FOLLOW_ID}',
                           headers={'Authorization': token},
                           content_type='application/json')
    USER.reload()
    assert response.status_code == 404
    assert response.json['message'] == 'User with given ID not found'


def test_unfollow_positive(client):
    USER = User.objects(id=1).first()
    USER_TO_UNFOLLOW = User.objects(id=5).first()
    token = login(client, 1)

    response = client.post(f'/api/unfollow/{USER_TO_UNFOLLOW.id}',
                           headers={'Authorization': token},
                           content_type='application/json')
    USER.reload()
    USER_TO_UNFOLLOW.reload()
    assert response.status_code == 200 or response.status_code == 202  # 202 if user already unfollowed


def test_unfollow_negative(client):
    USER = User.objects(id=1).first()
    USER_TO_UNFOLLOW = User.objects(id=5).first()
    token = login(client, 1)

    response = client.post(f'/api/unfollow/{USER_TO_UNFOLLOW.id}',
                           headers={'Authorization': token},
                           content_type='application/json')
    USER.reload()
    USER_TO_UNFOLLOW.reload()
    assert response.status_code == 202  # 202 if user already unfollowed


def test_unfollow_user_not_found(client):
    USER = User.objects(id=1).first()
    USER_TO_UNFOLLOW_ID = 6
    token = login(client, 1)

    response = client.post(f'/api/unfollow/{USER_TO_UNFOLLOW_ID}',
                           headers={'Authorization': token},
                           content_type='application/json')
    USER.reload()
    assert response.status_code == 404
