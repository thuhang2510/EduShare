from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.model.models import Account
 
class RegisterForm(FlaskForm):
    fullname = StringField('Tên đầy đủ', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    number = StringField('Số điện thoại', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), EqualTo('repassword', message='Mật khẩu và Nhập lại mật khẩu phải khớp nhau')])
    repassword = PasswordField('Nhập lại mật khẩu', validators=[DataRequired()])
    address = StringField('Địa chỉ')

    def validate_number(self, number):
        user = Account.query.filter_by(number=number.data).first()
        if user is not None:
            raise ValidationError('Số điện thoại này đã tồn tại')

    def validate_email(self, email):
        user = Account.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email này đã tồn tại')
        

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])

    def validate_email(self, email):
        user = Account.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email này chưa tồn tại')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
