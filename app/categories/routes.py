import os
from flask import jsonify, render_template, request, redirect
from flask_login import current_user
from app.categories import bp
from app.categories.services import CategoriesDataService

@bp.route("/", methods=["GET"])
def index():
    if 'parentId' in request.args:
        categories, _, msg = CategoriesDataService().get_by_parent_id(request.args['parentId'])
    else:
        categories, _, msg = CategoriesDataService().get_not_parent_id()

    if categories is None:
        return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'Lấy danh mục thành công', 'code': 0, 'data': categories})
