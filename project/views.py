import os
import uuid
from functools import wraps

from flask import request, jsonify, json
from itsdangerous import URLSafeSerializer as Serializer, BadSignature, SignatureExpired

from project.models import User, Post, Comment
from . import app

SECRET_KEY = os.environ.get('SECRET_KEY')  # secret key for token generation


# ---------------------------------- AUTHENTICATION MIDDLEWARE ---------------------------------------------------------
def auth_required(f):
    """
    Decorator to check if the request contains a valid token i.e it acts as a middleware for user authentication
    :param f: request handler function
    :return: requested handler function or json response with error message
    """

    @wraps(f)
    def auth_wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            try:
                serializer = Serializer(SECRET_KEY)
                data = serializer.loads(token, max_age=24 * 60 * 60)  # max_age is the expiration 24 hours
                return f(data, *args, **kwargs)
            except SignatureExpired:  # if token is expired
                return jsonify({'error': 'Token has expired'}), 401
            except BadSignature:  # if token is invalid
                return jsonify({'error': 'Invalid token'}), 401
        else:  # if token is missing in the request header
            return jsonify({'error': 'Token is missing'}), 400

    return auth_wrapper


# --------------------------------------------------------- USER Management --------------------------------------------


@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """
    # Checks if user exists and password is correct then returns a token in a json response,
    # email and password are taken from the request body via request.json
    # using plain passwords for the sake of simplicity for this assigment,
      in real world applications we should use hashing we could use flask-bcrypt or something similar
    """
    if not request.json or 'email' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Email or Password Missing'}), 400

    email = request.json.get('email')
    password = request.json.get('password')

    user = User.objects(email=email).first()
    if user and user.password == password:
        s = Serializer(SECRET_KEY)
        token = s.dumps({'email': user.email})
        return jsonify({'token': token}), 200

    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/user', methods=['GET'])
@auth_required
def get_user(data):
    """
    Authentication via token is required to access this route
    :param data: it is the data returned from the auth_required decorator that contains the email of the current user
    :return:json response containing username, number of followers and number of following of the current authenticated user
    """
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    json_data = {
        'username': current_user.name,
        'followers': len(current_user.followers),
        'following': len(current_user.following)
    }
    return jsonify(json_data), 200


@app.route('/api/follow/<id>', methods=['POST'])
@auth_required
def follow(data, id):
    """
    Authentication via token is required to access this route
    :param data: data returned from the auth_required decorator that contains the email of the current user
    :param id: id of the user to follow
    :return: json response containing a message
    """
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    user_to_follow = User.objects(id=id).first()
    if user_to_follow:
        if user_to_follow not in current_user.following:
            current_user.following.append(user_to_follow)  # add user to following list
            user_to_follow.followers.append(current_user)  # add user to followers list
            current_user.save()
            user_to_follow.save()
            return jsonify({'message': 'User followed successfully'}), 200
        else:
            return jsonify({'message': 'You already follow this user'}), 200
    else:
        return jsonify({'error': 'User with given ID not found'}), 404


@app.route('/api/unfollow/<id>', methods=['POST'])
@auth_required
def unfollow(data, id):
    """
    Authentication via token is required to access this route
    :param data: data returned from the auth_required decorator that contains the email of the current user
    :param id: id of the user to unfollow
    :return: json response containing a message
    """

    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    user_to_unfollow = User.objects(id=id).first()
    if user_to_unfollow:
        if user_to_unfollow in current_user.following:
            current_user.following.remove(user_to_unfollow)  # remove user from following list
            user_to_unfollow.followers.remove(current_user)  # remove user from followers list
            current_user.save()
            user_to_unfollow.save()
            return jsonify(
                {'message': f'Authenticated User  unfollowed {user_to_unfollow.name} with {id} successfully'}), 200
        else:
            return jsonify({'message': f'You are not following this user with id {id}'}), 200
    else:
        return jsonify({'error': f'User with given {id} not found'}), 404


# ------------------------------------------------- GET, CREATE, DELETE POSTS -----------------------------------------
@app.route('/api/all_posts', methods=['GET'])
def get_all_posts():
    """
    No need for authentication to access this route as it was not mentioned in the assignment
    :return: json response containing all posts with id,title, description, created time, comments and likes
    """
    posts = Post.objects()
    if posts:
        json_data = []
        for post in posts:
            comments = []
            # get all comments for the current post and append them to the comments list
            for comment in post.comments:
                comments.append(comment.text)
            # append the post data to the json_data list
            json_data.append({'id': str(post.id), 'title': post.title, 'desc': post.description,
                              'created_at': post.created_time, 'comments': comments, 'likes': len(post.likes)})

        return jsonify(json.loads(json.dumps(json_data, indent=4))), 200
    else:
        # return an error message if no posts found
        return jsonify({'error': 'No posts found'}), 404


@app.route('/api/posts', methods=['POST'])
@auth_required
def create_post(data):
    """
    Authentication via token is required to access this route
    create a post with title and description from the request body via request.json
    if title or description is missing return an error message with code 400

    :param data: data returned from the auth_required decorator that contains the email of the current user
    :return: json response containing the id, title, description and created time of the created post with code 201
    """

    if not request.json or 'title' not in request.json or 'description' not in request.json:
        return jsonify({'error': 'Title or description  is missing'}), 400

    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    # UTC time

    post = Post(title=request.json['title'], description=request.json['description'], author=current_user)
    post.save()
    post = Post.objects(id=post.id).first()

    return jsonify({'id': str(post.id), 'Title': post.title, 'Description': post.description,
                    'Created Time(UTC)': post.created_time}), 200


@app.route('/api/posts/<id>', methods=['GET'])
def get_post(id):
    """
    :param id: id of the post to get, don't need to be authenticated to access this route as it was not mentioned in the assignment
    :return: json response containing the id, title, description, number of likes and number of comments of the post
    """
    post = Post.objects(id=id).first()  # get post with given id
    if post:  # if post exists
        json_data = {
            'id': str(post.id),
            'title': post.title,
            'description': post.description,
            'likes': len(post.likes),
            'comments': len(post.comments)
        }
        return jsonify(json_data), 200
    else:
        # if post does not exists with given id, return response with code 404
        return jsonify({'error': 'Post with given id not found'}), 404


@app.route('/api/posts/<id>', methods=['DELETE'])
@auth_required
def delete_post(data, id):
    """
    Delete a post with given id from the database only if the current user is the author of the post
    if post does not exists with given id, it is assumed that the post is already deleted and return response with code 401
    :param data: data returned from the auth_required decorator that contains the email of the current user
    :param id: id of the post to delete
    :return: json response containing a message
    """

    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    post = Post.objects(id=id).first()

    if post:
        if post.author == current_user:  # check if the current user is the author of the post
            post.delete()
            return jsonify({'message': 'Post deleted successfully'}), 200
        else:
            # unauthorized user is trying to delete the post
            return jsonify({'error': 'You are not authorized to delete this post'}), 401
    else:
        # post with given id not found or post already deleted
        return jsonify({'message': 'Post with given id not found or Post already deleted'}), 404


# --------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------- LIKE AND UNLIKE POSTS --------------------------------------------
@app.route('/api/like/<id>', methods=['POST'])
@auth_required
def like_post(data, id):
    """
    Authenticated Users likes a post with given id
    :param data:
    :param id:
    :return:
        json response containing a message with code 200 if post liked successfully,
                                                     202 if  post is already liked by the user
                                                     404 if post with given id not found
    """

    post = Post.objects(id=id).first()
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    if post:
        if current_user and current_user not in post.likes:  # check if the user  not already liked the post
            post.likes.append(current_user)
            post.save()
            return jsonify({'message': 'Post liked successfully'}), 200
        else:
            # user already liked the post
            return jsonify({'message': 'You already liked this post'}), 200
    else:
        # post with given id not found
        return jsonify({'error': 'Post with given id not found'}), 404


@app.route('/api/unlike/<id>', methods=['POST'])
@auth_required
def unlike_post(data, id):
    """
    Authenticated Users unlikes a post with given id
    :param data:
    :param id:
    :return: json response containing a message with code 200 if post unliked successfully,
                                                          202 if  post is already unliked by the user
                                                          404 if post with given id not found

    """
    post = Post.objects(id=id).first()
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()  # get the current user
    if post:
        if current_user in post.likes:  # check if the user already unliked the post
            post.likes.remove(current_user)
            post.save()
            return jsonify({'message': 'Post unliked successfully'}), 200
        else:
            # user already unliked the post
            return jsonify({'message': 'You already unliked this post'}), 200
    else:
        # post with given id not found
        return jsonify({'error': 'Post with given id not found'}), 404


# ------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------- COMMENTS -----------------------------------------------------

@app.route('/api/comment/<id>', methods=['POST'])
@auth_required
def create_comment(data, id):
    """
    Authenticated User can comment on a post with given id
    :param data:
    :param id:
    :return:
        json response containing the {Comment-ID:<id>} of the comment with code
                                                                 201 if comment created successfully
                                                                 400 if 'comment' is missing in request body
                                                                 404 if post with given id not found
    """
    if not request.json or 'comment' not in request.json:
        return jsonify({'error': 'Comment is missing'}), 400
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    post = Post.objects(id=id).first()
    if post:
        comment = Comment()
        comment.user = current_user
        comment.text = request.json['comment']
        comment.id = str(uuid.uuid4())  # generate random id, guaranteed to be unique
        post.comments.append(comment)
        post.save()
        return jsonify({"Comment-ID": comment.id}), 200
    else:
        return jsonify({'error': 'Post with given id not found'}), 404
