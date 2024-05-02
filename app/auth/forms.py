from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.model.models import Account

import re
 
class RegisterForm(FlaskForm):
    fullname = StringField('Tên đầy đủ', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    cccd = StringField('Căn cước công dân', validators=[DataRequired(), Length(1, 12)])
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
        
    def validate_cccd(self, cccd):
        if(len(cccd.data) != 12):
            raise ValidationError('Căn cước công dân phải đúng 12 số')
        
        pattern =r"^[0-9]{12}$"
        if( not re.match(pattern, cccd.data)):
            raise ValidationError('Căn cước công dân không hợp lệ')

        user = Account.query.filter_by(cccd=cccd.data).first()
        if user is not None:
            raise ValidationError('Căn cước công dân này đã tồn tại')
        
    def validate_password(self, password):
        if(len(password.data) < 6):
            raise ValidationError('Mật khẩu phải có độ dài hơn 6 ký tự')
        
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])

    def validate_email(self, email):
        user = Account.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email này chưa tồn tại')
    
    def validate_password(self, password):
        user = Account.find_by_email(self.email.data)

        if(user.check_password(password.data) is False):
            raise ValidationError('Mật khẩu không đúng')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
