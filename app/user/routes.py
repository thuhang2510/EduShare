from flask import jsonify, render_template, request, redirect
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.user.forms import UpdateAccount, UpdatePassword
from app.user import bp
from app.user.services import UserDataService

@bp.route("/thong-tin-ca-nhan", methods=["GET"])
def index():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})
    return render_template('user/profile_user.html', title='User',form=register, formlogin=login, formresetpw=resetpw)

@bp.route("/upload-account", methods=["POST"])
def update_account():
    if current_user.is_authenticated:
        updateAccount = UpdateAccount(meta={'csrf': False})

        if updateAccount.validate():
            user, _, msg = UserDataService().update_account(current_user.id, updateAccount.data)

            if user is None:
                return jsonify({'message': 'Cập nhật tài khoản không thành công', 'code': -1, 'data': None})
            
            return jsonify({'message': 'Cập nhật tài khoản thành công', 'code': 0, 'data': user})
            
        return jsonify({'message': 'invalid input', 'code': -2, 'data': updateAccount.errors})

    return jsonify({'message': 'Hãy đăng nhập trước', 'code': -3, 'data': None})

@bp.route("/upload-password", methods=["POST"])
def update_password():
    if current_user.is_authenticated:
        updatePassword = UpdatePassword(meta={'csrf': False})

        if updatePassword.validate():
            user, _, msg = UserDataService().update_password(current_user.id, updatePassword.password.data)

            if user is None:
                return jsonify({'message': 'Cập nhật tài khoản không thành công', 'code': -1, 'data': None})
            
            return jsonify({'message': 'Cập nhật tài khoản thành công', 'code': 0, 'data': user})
            
        return jsonify({'message': 'invalid input', 'code': -2, 'data': updatePassword.errors})

    return jsonify({'message': 'Hãy đăng nhập trước', 'code': -3, 'data': None})
    