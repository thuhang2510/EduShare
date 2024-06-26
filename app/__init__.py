from flask import Flask
from flask_cors import CORS
from config import Config
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed
from app.extensions import celery_init_app, db, jwt, bootstrap, login, principals, mail, admin, babel

def get_locale():
    return 'vi'

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    jwt.init_app(app)
    bootstrap.init_app(app)
    login.init_app(app)
    admin.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    principals.init_app(app)
    mail.init_app(app)

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user

        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user, 'permission'):
            for permission in current_user.permission:
                identity.provides.add(RoleNeed(permission.name))

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.document import bp as document_bp
    app.register_blueprint(document_bp, url_prefix='/document')

    from app.categories import bp as categories_bp
    app.register_blueprint(categories_bp, url_prefix='/categories', name="user_categories")

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.evaluate import bp as evaluate_bp
    app.register_blueprint(evaluate_bp, url_prefix='/document/<int:document_id>/evaluate')

    from app.search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='')

    from app.ai import bp as ai_bp
    app.register_blueprint(ai_bp, url_prefix='/ai')

    from app.commitment import bp as commit_bp
    app.register_blueprint(commit_bp, url_prefix='/commitment')

    return app

from app.model import models