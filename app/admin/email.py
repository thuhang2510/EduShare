from flask import render_template
from app.email import send_email

def send_email_field(user):
    try:
        send_email(('[EduShare] Reset Your Password'),
                recipients=[user.email],
                html_body=render_template('email/update_field.html',
                                            user=user))
        
        return None, 0, "Send email success"
    except Exception as e:
        return None, -1, "Send email fail " + str(e) 