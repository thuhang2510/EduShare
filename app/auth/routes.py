from flask import abort, current_app, jsonify, render_template, session
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import RegisterForm, LoginForm, ResetPasswordRequestForm
from app.auth.services import UserDataService
from app.blacklist import BLACKLIST
from flask_login import current_user
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from app.categories.services import CategoriesDataService
from app.extensions import admin_permission, editter_permision
from flask_principal import identity_changed, Identity, AnonymousIdentity

@bp.route('/', methods=['GET'])
def index():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    categories, _, _ = CategoriesDataService().get_all_with_tuple()
    return render_template('home/trangchu.html', title='Trang chủ', form=register, formlogin=login, formresetpw=resetpw, categories=categories)

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
        
        identity=Identity(user.id)
        identity_changed.send(current_app._get_current_object(), identity=identity)
        
        access_token = create_access_token(user.id)
        return jsonify({'message': msg, 'code': 0, 'data': access_token})
        
    return jsonify({'message': 'Dữ liệu nhập vào không hợp lệ', 'code': -2, 'data': login.errors})


@bp.route('/thu')
@jwt_required()
@editter_permision.require()
def get_all_user():
    return "hihi"

@bp.route('/user-token')
def get_user_by_token():    
    if current_user.is_authenticated:
        data = {
            'id': current_user.id,
            'fullname': current_user.fullname,
            'email': current_user.email,
            'number': current_user.number,
            'coin': current_user.coin,
            'address': current_user.address,
            'datetime_week_reset': current_user.datetime_week_reset,
            'number_download': current_user.number_download,
            'datetime_day_reset': current_user.datetime_day_reset,
            'number_ask': current_user.number_ask
        }
        return jsonify({'message': 'Lấy user thành công', 'code': 0, 'data': data})
    
    return jsonify({'message': 'User chưa đăng nhập', 'code': -1, 'data': None}) 

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
    try:
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)

        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)

        identity_changed.send(current_app._get_current_object(),
                            identity=AnonymousIdentity())
        
        return jsonify({'message': 'Đăng xuất thành công', 'code': 0, 'data': None})
    except Exception as e:
        return jsonify({'message': 'Đăng xuất thất bại', 'code': -1, 'data': None})
