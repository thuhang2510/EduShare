from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, EqualTo

from app.model.models import Account

class UpdateAccount(FlaskForm):
    fullname = StringField(validators=[DataRequired()])
    address = StringField(validators=[DataRequired()])

class UpdatePassword(FlaskForm):
    oldpassword = StringField(validators=[DataRequired()])
    password = StringField(validators=[DataRequired(), EqualTo('repassword', message='Mật khẩu và Nhập lại mật khẩu phải khớp nhau')])
    repassword = StringField(validators=[DataRequired()])

    def validate_oldpassword(self, oldpassword):
        user = Account.find_by_id(current_user.id)

        if(user.check_password(oldpassword.data) is False):
            raise ValidationError('Mật khẩu cũ không đúng')
