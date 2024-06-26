from datetime import datetime
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import login_user, current_user, logout_user
from markupsafe import Markup
from app import db, admin
from app.admin.email import send_email_field, send_email_delete_doc
from app.admin.forms import CreateCategoryForm, EditCategoryForm, EditDocumentForm
from app.model.models import Account, Permission, Categories, Documents
from app.admin import bp
from app.auth.services import UserDataService

class AccountView(ModelView):
    can_view_details = True
    can_create = False
    can_delete = False
    column_hide_backrefs = False
    column_list = ('id', 'email', 'fullname', 'number', 'permission', 'number_ask', 'violation_count', 'premium', 'status')
    column_searchable_list = ('email', 'fullname', 'number')
    page_size = 10
    column_labels = dict(number='Số điện thoại', fullname='Họ và tên', permission='Quyền truy cập', status='Trạng thái', 
                         number_ask='SL hỏi', violation_count='SL vi phạm', premium="Số ngày Vip",
                         address='Địa chỉ', datetime_day_reset='Ngày bắt đầu', premium_start="Ngày bắt đầu gia hạn Vip")
    form_excluded_columns = ('password_hash', 'transaction', "evaluate", "document")
    column_details_exclude_list = ('password_hash', "evaluate", "document")
    column_details_list = ('id', 'email', 'fullname', 'number', 'permission', 'status', 'address', 
                   'number_ask', 'datetime_day_reset', 'violation_count', 'premium', 'premium_start')
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
    column_list = ("id", "document_name", "type",
                    "price", "download_count", "view_count", "processing_status", "status", "account", )
    column_details_list = ("id", "document_name", "type", "description",
                    "price", "download_count", "view_count", "image", "creation_date", "modified_date", "status", "account_id")
    column_labels = dict(document_name='Tên tài liệu', type='Loại', description='Mô tả',
                         price='Giá bán', download_count='SL tải', view_count='SL xem', image='Ảnh',
                         creation_date='Ngày tạo', modified_date='Ngày cập nhật', status='Trạng thái', account='Tên tài khoản', processing_status='Xử lý')
    form_excluded_columns = ("price", "download_count", "view_count", "image", 
                             "creation_date", "modified_date", "categories", "evaluate", "account")
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
    
    def _format_processing(view, context, model, name):
        if model.processing_status:
            return Markup('Thành công')
        elif model.processing_status == -1:
            return Markup('Thất bại')
        else:
            return Markup('Đang xử lý')

    def _format_image(view, context, model, name):
        if model.image == "/static/images/":
            return Markup(
            '<img src="/static/images/default_book.png" width="90" height="90">' % model.image
        )

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
        'modified_date': _format_modified_date, 
        'processing_status': _format_processing
    } 

    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
    def after_model_change(self, form, model, is_created):
        if not is_created:
            user = Account.find_by_id(model.account_id)
            send_email_delete_doc(model, user)
    
    @expose('/details/')
    def deltails(self):
        id = request.args.get("id")
        document = Documents.find_by_id(id)
        user = Account.find_by_id(document.account_id)
        return self.renderDetail('/admin/documents/detail.html', document=document, user=user)
    
    def renderDetail(self, template, **kwargs):
        self.extra_js = [url_for("static", filename="js/admin/detail.js")]
        return super(DocumentView, self).render(template, **kwargs)

    @expose('/edit/', methods=["GET", "POST"])
    def edit(self):
        id = request.args.get("id")
        document = Documents.find_by_id(id)
        user = Account.find_by_id(document.account_id)

        editDocument = EditDocumentForm(meta={'csrf': False})

        if request.method == 'GET':
            return self.renderEdit('/admin/documents/edit.html', form=editDocument, document=document, user=user)

        if editDocument.validate():
            if request.form.get("status") == 'on':
                document.status = True
                document.deletion_reason = None
                document.save_to_db()
                flash("Lưu lại tài liệu thành công")
            else:
                document.status = False
                document.deletion_reason = editDocument.deletion_reason.data
                document.save_to_db()
                flash("Xóa tài liệu thành công")
        
        return self.renderEdit('/admin/documents/edit.html', form=editDocument, document=document, user=user)
    
    def renderEdit(self, template, **kwargs):
        self.extra_js = [url_for("static", filename="js/admin/edit.js")]
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

            if (createCategory.data["parent_id"] != "null"):
                category.parent_id = createCategory.data["parent_id"]

            category.save_to_db()
            flash("Tạo danh mục thành công")
            categories_parent = Categories.find_all_parent()

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

            if (editCategory.data["parent_id"] != "null"):
                category.parent_id = editCategory.data["parent_id"]
            else:
                category.parent_id = None

            category.save_to_db()
            flash("Cập nhật danh mục thành công")

        return self.render('/admin/categories/edit.html', form=editCategory, category=category, categories_parent=categories_parent)
    
    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)

class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('/admin/stats/index.html')
    
    @expose("/stats-upload-document")
    def get_stats_upload_document(self):
        year = request.args.get('year', datetime.now().year, type=int)
        stats, code, msg = self._get_month_stats_upload_document(year)

        return jsonify({"message": msg, "code": code, "data": stats})

    def _get_month_stats_upload_document(self, year):  
        try:
            document = Documents.get_month_stats_all_document(year)
            keys = ("month", "count")
            results = []
            
            for transaction in document:
                results.append(dict(zip(keys, transaction)))
            
            return results, 0, "Get stats success"
        except Exception as e:
            return None, -1, "Get stats fail " + str(e)
        
    @expose("/stats-category")
    def get_stats_category(self):
        stats, code, msg = self._get_stats_category_doc()

        return jsonify({"message": msg, "code": code, "data": stats})

    def _get_stats_category_doc(self):  
        try:
            document = Categories.get_stats()
            keys = ("name", "count")
            results = []
            
            for transaction in document:
                results.append(dict(zip(keys, transaction)))
            
            return results, 0, "Get stats success"
        except Exception as e:
            return None, -1, "Get stats fail " + str(e)
    
    def is_accessible(self):
        return current_user.is_authenticated and any(obj.name == 'admin' for obj in current_user.permission)
    
admin.add_view(AccountView(Account, db.session, name="Người dùng"))
admin.add_view(PermissionView(Permission, db.session, name="Quyền"))
admin.add_view(DocumentView(Documents, db.session, name="Tài liệu"))
admin.add_view(CategoryView(name="Danh mục", endpoint="categories"))
admin.add_view(StatsView(name="Thống kê", endpoint="stats"))
admin.add_view(LogoutView(name="Đăng xuất"))

@bp.route("/admin-login", methods=["POST"])
def loginAdmin():
    email = request.form.get('email')
    password = request.form.get('password')

    user, code, msg = UserDataService().get_by_email(email)
        
    if user is not None and user.check_password(password) and any(obj.name == 'admin' for obj in user.permission):        
        login_user(user)

    return redirect('/admin')