import uuid
from functools import wraps

from flask import request, jsonify
from itsdangerous import URLSafeSerializer as Serializer, BadSignature, SignatureExpired

from project.models import User, Post, Comment
from . import app


def auth_required(f):
    @wraps(f)
    def auth_wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            try:
                serializer = Serializer('123')
                data = serializer.loads(token, max_age=24 * 60 * 60)
                return f(data, *args, **kwargs)
            except SignatureExpired:
                return jsonify({'error': 'Token has expired'}), 401
            except BadSignature:
                return jsonify({'error': 'Invalid token'}), 401
        else:
            return jsonify({'error': 'Token is missing'}), 401

    return auth_wrapper


@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.objects(email=email).first()
    if user and user.password == password:
        s = Serializer('123')
        token = s.dumps({'email': user.email})

        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/user', methods=['GET'])
@auth_required
def get_user(data):
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    json_data = {
        'User Name': current_user.name,
        'followers': len(current_user.followers),
        'following': len(current_user.following)
    }
    return jsonify(json_data), 200


@app.route('/api/follow/<id>', methods=['POST', 'GET'])
@auth_required
def follow(data, id):
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    user_to_follow = User.objects(id=id).first()
    if user_to_follow:
        if user_to_follow not in current_user.following:
            current_user.following.append(user_to_follow)
            user_to_follow.followers.append(current_user)
            current_user.save()
            user_to_follow.save()
            return jsonify({'message': 'User followed successfully'}), 200
        else:
            return jsonify({'message': 'You already follow this user'}), 202
    else:
        return jsonify({'message': 'User with given ID not found'}), 404


@app.route('/api/unfollow/<id>', methods=['POST'])
@auth_required
def unfollow(data, id):
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    user_to_unfollow = User.objects(id=id).first()
    if user_to_unfollow:
        if user_to_unfollow in current_user.following:
            current_user.following.remove(user_to_unfollow)
            user_to_unfollow.followers.remove(current_user)
            current_user.save()
            user_to_unfollow.save()
            return jsonify(
                {'message': f'Authenticated User  unfollowed {user_to_unfollow.name} with {id} successfully'}), 200
        else:
            return jsonify({'message': f'You are not following this user with id {id}'}), 202
    else:
        return jsonify({'message': f'User with given {id} not found'}), 404


# ------------------------------------------------- GET, CREATE, DELETE POSTS -----------------------------------------
@app.route('/api/all_posts', methods=['GET'])
def get_all_posts():
    posts = Post.objects()
    if posts:
        json_data = []
        for post in posts:
            comments = []
            for comment in post.comments:
                comments.append(comment.text)

            json_data.append({'id': str(post.id), 'title': post.title, 'desc': post.description,
                              'created_at': post.created_time, 'comments': comments, 'likes': len(post.likes)})

        return jsonify(json_data), 200
    else:
        return jsonify({'message': 'No posts found'}), 404


@app.route('/api/posts', methods=['POST'])
@auth_required
def create_post(data):
    if not request.json or 'title' not in request.json or 'description' not in request.json:
        return jsonify({'error': 'Title or description  is missing'}), 400
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    # UTC time

    post = Post(title=request.json['title'], description=request.json['description'], author=current_user)
    post.save()
    post = Post.objects(id=post.id).first()

    return jsonify({'id': str(post.id), 'Title': post.title, 'Description': post.description,
                    'Created Time(UTC)': post.created_time}), 201


@app.route('/api/posts/<id>', methods=['GET'])
def get_post(id):
    post = Post.objects(id=id).first()
    if post:
        json_data = {
            'id': str(post.id),
            'title': post.title,
            'description': post.description,
            'likes': len(post.likes),
            'comments': len(post.comments)
        }
        return jsonify(json_data), 200
    else:
        return jsonify({'message': 'Post with given id not found'}), 404


@app.route('/api/posts/<id>', methods=['DELETE'])
@auth_required
def delete_post(data, id):
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    post = Post.objects(id=id).first()

    if post:
        if post.author == current_user:
            post.delete()
            return jsonify({'message': 'Post deleted successfully'}), 200
        else:
            return jsonify({'message': 'You are not authorized to delete this post'}), 401
    else:
        return jsonify({'message': 'Post with given id not found or Post already deleted'}), 401


# --------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------- LIKE AND UNLIKE POSTS --------------------------------------------
@app.route('/api/like/<id>', methods=['POST'])
@auth_required
def like_post(data, id):
    post = Post.objects(id=id).first()
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    if post:
        if current_user and current_user not in post.likes:
            post.likes.append(current_user)
            post.save()
            return jsonify({'message': 'Post liked successfully'}), 200
        else:
            return jsonify({'message': 'You already liked this post'}), 202
    else:
        return jsonify({'message': 'Post with given id not found'}), 404


@app.route('/api/unlike/<id>', methods=['POST'])
@auth_required
def unlike_post(data, id):
    post = Post.objects(id=id).first()
    current_user_email = data['email']
    current_user = User.objects(email=current_user_email).first()
    if post:
        if current_user in post.likes:
            post.likes.remove(current_user)
            post.save()
            return jsonify({'message': 'Post unliked successfully'}), 200
        else:
            return jsonify({'message': 'You already unliked this post'}), 202
    else:
        return jsonify({'message': 'Post with given id not found'}), 404


# ------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------- COMMENTS -----------------------------------------------------

@app.route('/api/comment/<id>', methods=['POST'])
@auth_required
def create_comment(data, id):
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
        return jsonify({"Comment-ID": comment.id}), 201
    else:
        return jsonify({'message': 'Post with given id not found'}), 404
