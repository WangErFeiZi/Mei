from flask import jsonify, url_for, request, current_app, g
from . import api
from .errors import forbidden, unauthorized
from .. import db
from ..models import Permission, Role, User, Post, Comment
from .decorators import permission_required
from .authentication import auth


@api.route('/posts/')
@auth.login_required
def get_posts():
    if g.current_user.is_anonymous:
        return unauthorized('is anonymous 游客无法浏览该页.')
    page = request.args.get('page', 1,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).\
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


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
           {'location': url_for('api.get_post', id=post.id, _external=True)}


@api.route('/posts/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author_id and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions 没有足够的权限.')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())






