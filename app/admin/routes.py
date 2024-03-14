from flask import jsonify, redirect, request
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import login_user, current_user, logout_user
from app import db, admin
from app.admin.email import send_email_field
from app.model.models import Account, Permission
from app.admin import bp
from app.auth.services import UserDataService

class AccountView(ModelView):
    can_view_details = True
    can_create = False
    can_delete = False
    column_hide_backrefs = False
    column_list = ('id', 'email', 'fullname', 'number', 'permission', 'coin', 
                   'number_download', 'number_ask', 'violation_count', 'status')
    column_searchable_list = ('email', 'fullname', 'number')
    page_size = 10
    column_labels = dict(number='Số điện thoại', fullname='Họ và tên', permission='Quyền truy cập', status='Trạng thái', 
                         coin='Số tiền', number_download='SL tải', number_ask='SL hỏi', violation_count='SL vi phạm',
                         address='Địa chỉ', datetime_day_reset='Ngày bắt đầu', datetime_week_reset='Tuần bắt đầu')
    form_excluded_columns = ('password_hash', 'transaction')
    column_details_exclude_list = ('password_hash')
    column_details_list = ('id', 'email', 'fullname', 'number', 'permission', 'status', 'coin', 'address', 
                   'number_download', 'number_ask', 'datetime_week_reset', 'datetime_day_reset', 'violation_count')
    column_editable_list = ('fullname', 'permission', 'status')
    form_widget_args = {
        'email': {
            'readonly': True
        },
        'number': {
            'readonly': True
        }
    }

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
    def after_model_change(self, form, model, is_created):
        if not is_created:
            send_email_field(model)
    
class PermissionView(ModelView):
    column_display_pk = True
    can_delete = False
    column_labels = dict(name='Tên quyền', description='Mô tả')

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')
    
    def is_accessible(self):
        return current_user.is_authenticated

admin.add_view(AccountView(Account, db.session, name="Người dùng"))
admin.add_view(PermissionView(Permission, db.session, name="Quyền"))
admin.add_view(LogoutView(name="Đăng xuất"))

@bp.route("/admin-login", methods=["POST"])
def loginAdmin():
    email = request.form.get('email')
    password = request.form.get('password')

    user, code, msg = UserDataService().get_by_email(email)
        
    if user is not None and user.check_password(password) and any(obj.name == 'admin' for obj in user.permission):        
        login_user(user)

    return redirect('/admin')