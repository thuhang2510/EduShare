from flask_principal import Permission, RoleNeed, Principal
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_mail import Mail
from flask_admin import Admin
from flask_babel import Babel

from app.blacklist import BLACKLIST

bootstrap = Bootstrap()
login = LoginManager()
db = SQLAlchemy()
jwt = JWTManager()
principals = Principal()
mail = Mail()
admin = Admin(name='Quản trị EduShare', template_mode='bootstrap4')
babel = Babel()

admin_permission = Permission(RoleNeed('admin'))
reporter_permission = Permission(RoleNeed('reporter'))
uploader_permission = Permission(RoleNeed('uploader'))
downloader_permission = Permission(RoleNeed('downloader'))
editter_permision = Permission(RoleNeed('editter'))

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    return (jti in BLACKLIST)

@login.user_loader
def load_user(user_id):
    from app.model.models import User

    return User.query.get(user_id)

@login.request_loader
@jwt_required(optional=True)
def load_user_from_request(request):
    from app.model.models import User

    api_key = request.headers.get('Authorization')
    if api_key:
        try:
            id = get_jwt_identity()
            print("User ID:", id)
        except TypeError:
            pass
        user = User.query.filter_by(id=id).first()
        if user:
            return user

    return None