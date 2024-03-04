from flask import Flask
from config import Config
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed
from app.extensions import db, jwt, bootstrap, login, principals, mail, admin, babel

def get_locale():
    return 'vi'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    jwt.init_app(app)
    bootstrap.init_app(app)
    login.init_app(app)
    admin.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    principals.init_app(app)
    mail.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user

        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.momo import bp as momo_bp
    app.register_blueprint(momo_bp, url_prefix='/momo')

    return app

from app.model import models