from flask import jsonify, url_for, request, current_app, g
from . import api
from .errors import forbidden
from .. import db
from ..models import Permission, Role, User, Post, Comment
from .decorators import permission_required
from .authentication import auth


@api.route('/users/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get_or_404(id=id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/posts/')
@auth.login_required
def get_user_posts(id):
    if g.current_user.is_anonymous:
        return forbidden('is anonymous 游客无法浏览该页.')
    user = User.query.get_or_404(id=id)
    page = request.args.get('page', 1,type=int)
    pagination = user.posts.query.order_by(Post.timestamp.desc()).\
        paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({'posts': [post.to_json() for post in posts],
                    'prev': prev,
                    'next': next,
                    'count': pagination.total})


@api.route('/users/<int:id>/timeline/')
@auth.login_required
def get_user_followed_posts(id):
    if g.current_user.is_anonymous:
        return forbidden('is anonymous 游客无法浏览该页.')
    user = User.query.get_or_404(id=id)
    page = request.args.get('page', 1,type=int)
    pagination = user.followed_posts.query.order_by(Post.timestamp.desc*()).\
        paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({'posts': [post.to_json() for post in posts],
                    'prev': prev,
                    'next': next,
                    'count': pagination.total})




