from flask import render_template, request, redirect
from flask_login import current_user
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.momo import bp

@bp.route("/document", methods=["GET"])
def document():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})
    return render_template('document/document_detail.html', title='Document',form=register, formlogin=login, formresetpw=resetpw)