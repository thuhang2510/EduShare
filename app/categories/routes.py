from flask import jsonify, render_template, request
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.categories import bp
from app.categories.services import CategoriesDataService
from app.document.services import DocumentsDataService

@bp.route("/", methods=["GET"])
def index():
    if 'parentId' in request.args:
        categories, _, msg = CategoriesDataService().get_by_parent_id(request.args['parentId'])
    else:
        categories, _, msg = CategoriesDataService().get_not_parent_id()

    if categories is None:
        return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'Lấy danh mục thành công', 'code': 0, 'data': categories})

@bp.route("/all", methods=["GET"])
def get_all():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    categories, _, _ = CategoriesDataService().get_all_with_tuple()

    return render_template('categories/all_categories.html', form=register, 
                           formlogin=login, formresetpw=resetpw, categories=categories)

@bp.route('/<category_name>')
def category_view(category_name):
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    page = request.args.get('page', 1, type=int)

    documents, _, _ = DocumentsDataService().get_by_category_with_paginate(category_name, 15, page)
    return render_template('categories/detail.html', form=register, 
                           formlogin=login, formresetpw=resetpw, documents=documents, category_name=category_name)
