from flask import current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body,
               attachments=None, sync=False):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            with current_app.open_resource(attachment[0]) as fp:
                msg.attach(attachment[0], attachment[1], fp.read())
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()
