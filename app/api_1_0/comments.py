from flask import jsonify, url_for, request, current_app, g
from . import api
from .errors import forbidden
from .. import db
from ..models import Permission, Role, User, Post, Comment
from .decorators import permission_required
from .authentication import auth


@api.route('/comments/')
@auth.login_required
def get_comments():
    if g.current_user.is_anonymous:
        return forbidden('is anonymous 游客无法浏览该页.')
    page = request.args.get('page', 1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).\
        paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({'comments': [comments.to_json() for comments in comments],
                    'prev': prev,
                    'next': next,
                    'count': pagination.total})


@api.route('/comments/<int:id>')
@auth.login_required
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/')
@auth.login_required
def get_post_comments():
    if g.current_user.is_anonymous:
        return forbidden('is anonymous 游客无法浏览该页.')
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1,type=int)
    pagination = post.comments.query.order_by(Comment.timestamp.desc()).\
        paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_post_comments', page=page+1, _external=True)
    return jsonify({'comments': [comments.to_json() for comments in comments],
                    'prev': prev,
                    'next': next,
                    'count': pagination.total})


@api.route('/posts/<int:id>/comments/')
@auth.login_required
@permission_required(Permission.COMMENT)
def new_post_comments(id):
    if g.current_user.is_anonymous:
        return forbidden('is anonymous 游客无法浏览该页.')
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'location': url_for('api.get_comment', id=comment.id)}




