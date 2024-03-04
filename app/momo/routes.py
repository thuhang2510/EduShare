from flask_login import current_user
from app.auth import bp
from app.momo.email import send_email_field

@bp.route("/send-mail", methods=["GET"])
def sendMail():
    send_email_field(current_user)