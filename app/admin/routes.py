from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import login_user, current_user, logout_user
from markupsafe import Markup
from app import db, admin
from app.admin.email import send_email_field
from app.admin.forms import CreateCategoryForm, EditCategoryForm
from app.model.models import Account, Permission, Categories, Documents, Transaction
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
    form_excluded_columns = ('password_hash', 'transaction', "evaluate", "purchase")
    column_details_exclude_list = ('password_hash', "evaluate", "purchase")
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
    edit_template = "/admin/edit.html"
    list_template = "/admin/list.html"
    details_template = "/admin/detail.html"

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
    def after_model_change(self, form, model, is_created):
        if not is_created:
            send_email_field(model)
    
class PermissionView(ModelView):
    column_display_pk = True
    can_delete = False
    column_labels = dict(name='Tên quyền', description='Mô tả')
    form_excluded_columns = ("account")

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
    edit_template = "/admin/edit.html"
    list_template = "/admin/list.html"
    details_template = "/admin/detail.html"
    
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')
    
    def is_accessible(self):
        return current_user.is_authenticated

class DocumentView(ModelView):
    column_display_pk = True
    can_view_details = True
    can_create = False
    can_edit = True
    can_delete = False
    column_searchable_list = ('document_name', 'id')
    column_list = ("id", "document_name", "type", "description",
                    "price", "download_count", "view_count", "image", "status", "account")
    column_details_list = ("id", "document_name", "type", "description",
                    "price", "download_count", "view_count", "image", "creation_date", "modified_date", "status", "account_id")
    column_labels = dict(document_name='Tên tài liệu', type='Loại', description='Mô tả',
                         price='Giá bán', download_count='SL tải', view_count='SL xem', image='Ảnh',
                         creation_date='Ngày tạo', modified_date='Ngày cập nhật', status='Trạng thái', account='Tên tài khoản')
    form_excluded_columns = ("price", "download_count", "view_count", "image", 
                             "creation_date", "modified_date", "categories", "evaluate", "purchase", "account")
    form_widget_args = {
        'document_name': {
            'readonly': True
        },
        'type': {
            'readonly': True
        },
        'description': {
            'readonly': True
        }
    }
    edit_template = "/admin/edit.html"
    list_template = "/admin/list.html"

    def _format_document_name(view, context, model, name):
        if not model.document_name:
            return ''

        return Markup(
            model.document_name.rsplit(".", 1)[0]
        )

    def _format_image(view, context, model, name):
        if not model.image:
            return ''

        return Markup(
            '<img src="%s" width="90" height="90">' % model.image
        )
    
    def _format_creation_date(view, context, model, name):
        if not model.creation_date:
            return ''

        return Markup(
            model.creation_date.strftime('%d-%m-%Y %H:%M:%S')
        )

    def _format_modified_date(view, context, model, name):
        if not model.modified_date:
            return ''

        return Markup(
            model.modified_date.strftime('%d-%m-%Y %H:%M:%S')
        )

    column_formatters = {
        'document_name': _format_document_name,
        'image': _format_image,
        'creation_date': _format_creation_date,
        'modified_date': _format_modified_date
    } 

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
    @expose('/details/')
    def deltails(self):
        id = request.args.get("id")
        document = Documents.find_by_id(id)
        user = Account.find_by_id(document.account_id)
        return self.render('/admin/documents/detail.html', document=document, user=user)
    
    def render(self, template, **kwargs):
        self.extra_js = [url_for("static", filename="js/admin/detail.js")]

        return super(DocumentView, self).render(template, **kwargs)
    
class CategoryView(BaseView):    
    @expose('/')
    def index(self):
        search = request.args.get('search')
        categories =  Categories.find_with_name(search)
        return self.render('/admin/categories/index.html', categories=categories)
    
    @expose("/create", methods=["GET", "POST"])
    def create(self):    
        createCategory = CreateCategoryForm(meta={'csrf': False})
        categories_parent = Categories.find_all_parent()

        if request.method == 'GET':
            return self.render('/admin/categories/new.html', form=createCategory, categories_parent=categories_parent)

        category = None
        if createCategory.validate():
            category =  Categories()
            category.name = createCategory.data["name"]
            category.description = createCategory.data["description"]
            category.parent_id = createCategory.data["parent_id"]
            category.save_to_db()
            flash("Tạo danh mục thành công")

        return self.render('/admin/categories/new.html', form=createCategory, category=category, categories_parent=categories_parent)
    
    @expose("/details", methods=["GET"])
    def detail(self):
        id = request.args.get("id")
        category = Categories.find_by_id(id)
        category_parent = Categories.find_by_id(category.parent_id)

        return self.render('/admin/categories/detail.html', category=category, category_parent=category_parent)
    
    @expose("/edit", methods=["GET", "POST"])
    def edit(self):
        id = request.args.get("id")

        categories_parent = Categories.find_all_parent()
        category = Categories.find_by_id(id)
        editCategory = EditCategoryForm(meta={'csrf': False})
        editCategory.id = id

        if request.method == 'GET':
            return self.render('/admin/categories/edit.html', form=editCategory, category=category, categories_parent=categories_parent)

        if editCategory.validate():
            category.name = editCategory.data["name"]
            category.description = editCategory.data["description"]
            category.parent_id = editCategory.data["parent_id"]
            category.save_to_db()
            flash("Cập nhật danh mục thành công")

        return self.render('/admin/categories/edit.html', form=editCategory, category=category, categories_parent=categories_parent)
    
    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)

class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('/admin/stats/index.html')
    
    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
class TransactionView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_display_pk = True
    column_filters = ('date', 'type', 'id', 'result')
    column_labels = dict(information='Thông tin', type='Loại', amount='Số tiền',
                         wallet_balance='Số dư tài khoản', result='Kết quả', account='Tài khoản',
                         date='Ngày giao dịch', status='Trạng thái')
    list_template = "/admin/list.html"
    details_template = "/admin/detail.html"

    def _format_date(view, context, model, name):
        if not model.date:
            return ''

        return Markup(
            model.date.strftime('%d-%m-%Y %H:%M:%S')
        )
    
    def _format_result(view, context, model, name):
        if model.result == 0:
            result_show = "Thành công"
        else:
            result_show = "Thất bại"

        return Markup(
            result_show
        )

    column_formatters = {
        'date': _format_date,
        'result': _format_result
    } 

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
admin.add_view(AccountView(Account, db.session, name="Người dùng"))
admin.add_view(PermissionView(Permission, db.session, name="Quyền"))
admin.add_view(DocumentView(Documents, db.session, name="Tài liệu"))
admin.add_view(CategoryView(name="Danh mục", endpoint="categories"))
admin.add_view(TransactionView(Transaction, db.session, name="Giao dịch"))
admin.add_view(StatsView(name="Thống kê"))
admin.add_view(LogoutView(name="Đăng xuất"))

@bp.route("/admin-login", methods=["POST"])
def loginAdmin():
    email = request.form.get('email')
    password = request.form.get('password')

    user, code, msg = UserDataService().get_by_email(email)
        
    if user is not None and user.check_password(password) and any(obj.name == 'admin' for obj in user.permission):        
        login_user(user)

    return redirect('/admin')