from flask import Blueprint
from jwt import InvalidTokenError, ExpiredSignatureError
from flask_jwt_extended.exceptions import (
    NoAuthorizationError, InvalidHeaderError, WrongTokenError,
    RevokedTokenError)

bp = Blueprint('purchase', __name__)

@bp.errorhandler(403)
def handle_auth_error(e):
    return {'message': 'Bạn không có quyền thực hiện chức năng này.', 'code': -4}, 403

@bp.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    return {'message': 'Bạn không có quyền truy cập vào tài nguyên này. Vui lòng đăng nhập để tiếp tục', 'code': -4}, 401

@bp.errorhandler(RevokedTokenError)
def handle_expired_error(e):
    return {'message': 'Chúng tôi rất tiếc nhưng phiên của bạn đã hết hạn. Vui lòng đăng nhập lại để tiếp tục', 'code': -4}, 401

@bp.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return {'message': str(e), 'code': -1}, 422


@bp.errorhandler(InvalidTokenError)
def handle_invalid_token_error(e):
    return {'message': 'Đã xảy ra lỗi với mã thông báo truy cập của bạn. Mã thông báo không hợp lệ. Vui lòng đăng nhập lại để tiếp tục', 'code': -4}, 422

@bp.errorhandler(ExpiredSignatureError)
def handle_invalid_token_error(e):
    return {'message': 'Đã xảy ra lỗi với mã thông báo truy cập của bạn. Mã thông báo đã hết hạn. Vui lòng đăng nhập lại để tiếp tục', 'code': -4}, 422

@bp.errorhandler(WrongTokenError)
def handle_wrong_token_error(e):
    return {'message': str(e), 'code': -4}, 422

from app.purchase import routes