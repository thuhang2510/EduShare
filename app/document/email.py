from flask import render_template
from app.email import send_email

def send_report(document, user, recipient, content, attachment):
    try:
        send_email(('[EduShare] Báo cáo' + document["document_name"]),
                recipients=[recipient],
                html_body=render_template('email/report.html', content=content,
                                            user=user, document=document),
                attachments=[attachment])
        
        return None, 0, "Send email success"
    except Exception as e:
        return None, -1, "Send email fail " + str(e) 
