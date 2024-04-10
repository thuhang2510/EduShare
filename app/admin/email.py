from flask import render_template
from app.email import send_email

def send_email_field(user):
    try:
        send_email(('[EduShare] Cập nhật thông tin tài khoản'),
                recipients=[user.email],
                html_body=render_template('email/update_field.html',
                                            user=user))
        
        return None, 0, "Send email success"
    except Exception as e:
        return None, -1, "Send email fail " + str(e) 
    
def send_email_delete_doc(document, user):
    try:
        send_email(('[EduShare] Xóa tài liệu'),
                recipients=[user.email],
                html_body=render_template('email/delete_doc.html',
                                            user=user, document=document))
        
        return None, 0, "Send email success"
    except Exception as e:
        return None, -1, "Send email fail " + str(e) 