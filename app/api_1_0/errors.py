from app.exceptions import ValidationError
from . import api
from flask import jsonify


def bad_request(message):
    response = jsonify({'error': 'bad request 请求错误', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized 授权失败', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden 页面禁止', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


