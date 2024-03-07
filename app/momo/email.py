from flask import render_template
from app.email import send_email

def send_email_field(user, transaction):
    try:
        send_email(('[EduShare] Thông báo nạp tiền'),
                recipients=[user.email],
                html_body=render_template('email/recharge.html',
                                            user=user, transaction=transaction))
        
        return None, 0, "Send email success"
    except Exception as e:
        print(str(e))
        return None, -1, "Send email fail " + str(e) 