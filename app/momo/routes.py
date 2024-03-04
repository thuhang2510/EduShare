from flask_login import current_user
from app.momo import bp
from app.model.models import User
from app.momo.email import send_email_field

@bp.route("/sendmail", methods=["GET"])
def guiMail():
    user = User()
    user.fullname = "ha"
    user.email = "thu"
    user.number = "131313"
    user.set_password("hang")
    user.save_to_db()

    return None

@bp.route("/")
def index():
    return "hihi"