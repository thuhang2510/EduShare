from flask import jsonify, render_template
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import RegisterForm, LoginForm, ResetPasswordRequestForm
from app.auth.services import UserDataService
from app.blacklist import BLACKLIST
from flask_login import login_user, current_user
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from app.extensions import admin_permission, editter_permision

@bp.route('/', methods=['GET'])
def index():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})
    return render_template('auth/register.html', title='Đăng ký', form=register, formlogin=login, formresetpw=resetpw)

@bp.route('/register', methods=['POST'])
def register():
    register = RegisterForm(meta={'csrf': False})

    if register.validate():
        data, code, msg = UserDataService().create(register.data)

        if(code == 0):
            return jsonify({'message': msg, 'code': 0, 'data': data.to_dict()})
        else:
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'invalid input', 'code': -2, 'data': register.errors})

@bp.route('/login', methods=['POST'])
def login():
    login = LoginForm(meta={'csrf': False})

    if login.validate():
        user, _, msg = UserDataService().get_by_email(login.email.data)
        
        if user is None or not user.check_password(login.password.data):
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
        '''
        login_user(user)
        print(current_user)

        identity=Identity(user.id)
        identity_changed.send(current_app._get_current_object(), identity=identity)
        '''

        login_user(user)
        access_token = create_access_token(user.id)
        return jsonify({'message': msg, 'code': 0, 'data': access_token})
        
    return jsonify({'message': 'Dữ liệu nhập vào không hợp lệ', 'code': -2, 'data': login.errors})


@bp.route('/thu')
@jwt_required()
@editter_permision.require()
def get_all_user():
    return "hihi"

@bp.route('/resetpw', methods=['POST'])
def resetpw():
    if current_user.is_authenticated:
        return jsonify({'message': 'Bạn đã đăng nhập', 'code': -1, 'data': None})

    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    if resetpw.validate():
        user, _, msg = UserDataService().get_by_email(resetpw.email.data)

        if user is None:
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
        send_password_reset_email(user)
        return jsonify({'message': 'Mật khẩu đã gửi qua mail', 'code': 0, 'data': None})

    return jsonify({'message': 'Dữ liệu nhập vào không hợp lệ', 'code': -2, 'data': resetpw.errors})

@bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return jsonify(msg="Access token revoked")