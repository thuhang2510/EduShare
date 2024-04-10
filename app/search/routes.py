from datetime import datetime
from flask import jsonify, render_template, request, redirect, json, send_file, send_from_directory
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.search import bp
from app.document.services import DocumentsDataService
from app.categories.services import CategoriesDataService

@bp.route('/search-documents', methods=['GET'])
def search_documents_route():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    page = request.args.get('page', 1, type=int)
    query = request.args.get('query')
    sort = request.args.get('sort', 0, int)
    is_sell = request.args.get('is_sell', 0, int)
    cat_id = request.args.get('cat_id', 0, int)
    cat_name = request.args.get('cat_name', 'Tất cả', str)

    documents, _, _ = DocumentsDataService().search_documents(page, query, sort, is_sell, cat_id)
    categories, _, _ = CategoriesDataService().get_all_with_tuple()

    return render_template('home/search.html', title='Tìm kiếm', form=register, 
                           formlogin=login, formresetpw=resetpw, categories=categories, 
                           documents=documents, query=query, sort=sort, is_sell=is_sell, cat_id=cat_id, cat_name=cat_name)
