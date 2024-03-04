from flask_login import current_user
from app.auth import bp
from app.model.models import User
from app.momo.email import send_email_field

@bp.route("/send-mail", methods=["GET"])
def sendMail():
    user = User()
    user.email = "thu"
    user.number = "131313"
    user.set_password("hang")
    user.save_to_db()