from flask import Blueprint, jsonify
from jwt import InvalidTokenError, ExpiredSignatureError
from flask_jwt_extended.exceptions import (
    JWTDecodeError, NoAuthorizationError, InvalidHeaderError, WrongTokenError,
    RevokedTokenError)

bp = Blueprint('auth', __name__)

@bp.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    return {'message': 'Bạn không có quyền truy cập vào tài nguyên này.', 'code': -4}, 401

@bp.errorhandler(RevokedTokenError)
def handle_expired_error(e):
    return {'message': 'Chúng tôi rất tiếc nhưng phiên của bạn đã hết hạn. Vui lòng đăng nhập lại để tiếp tục', 'code': -4}, 401

@bp.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return {'message': str(e), 'code': -4}, 422


@bp.errorhandler(InvalidTokenError)
def handle_invalid_token_error(e):
    return {'message': 'Đã xảy ra lỗi với mã thông báo truy cập của bạn. Mã thông báo không hợp lệ. Vui lòng đăng nhập lại để tiếp tục', 'code': -4}, 422

@bp.errorhandler(ExpiredSignatureError)
def handle_invalid_token_error(e):
    return {'message': 'Đã xảy ra lỗi với mã thông báo truy cập của bạn. Mã thông báo đã hết hạn. Vui lòng đăng nhập lại để tiếp tục', 'code': -4}, 422

@bp.errorhandler(JWTDecodeError)
def handle_jwt_decode_error(e):
    return {'message': str(e), 'code': -4}, 422


@bp.errorhandler(WrongTokenError)
def handle_wrong_token_error(e):
    return {'message': str(e), 'code': -4}, 422

@bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'message': 'Yêu cầu của bạn bị trừ chối vì bạn không được phép truy cập tài nguyên này. Vui lòng đăng nhập bằng tài khoản có quyền phù hợp.', 'code': -4}), 401

from app.auth import routes