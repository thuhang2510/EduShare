import random
import string
from flask import render_template
from app.email import send_email
from app.auth.services import UserDataService

def send_password_reset_email(user):
    password = create_password(8)
    data, code, msg = UserDataService().update_password(user.id, password)

    if data is None:
        return data, code, msg

    try:
        send_email(('[EduShare] Reset Your Password'),
                recipients=[user.email],
                html_body=render_template('email/reset_password.html',
                                            user=user, token=password))
        
        return None, 0, "Send email success"
    except Exception as e:
        return None, -1, "Send email fail " + str(e) 
    
def create_password(size):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))
