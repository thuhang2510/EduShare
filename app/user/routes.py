from datetime import datetime
from flask import jsonify, render_template, request, redirect
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.user.forms import UpdateAccount, UpdatePassword
from app.user import bp
from app.user.services import UserDataService
from app.document.services import DocumentsDataService
from app.transaction.services import TransactionDataService

@bp.route("/thong-tin-ca-nhan", methods=["GET"])
def index():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})
    return render_template('user/profile_user.html', title='User',form=register, formlogin=login, formresetpw=resetpw)

@bp.route("/upload-account", methods=["POST"])
@jwt_required()
def update_account():
    updateAccount = UpdateAccount(meta={'csrf': False})

    if updateAccount.validate():
        user, _, msg = UserDataService().update_account(current_user.id, updateAccount.data)

        if user is None:
            return jsonify({'message': 'Cập nhật tài khoản không thành công', 'code': -1, 'data': None})
        return jsonify({'message': 'Cập nhật tài khoản thành công', 'code': 0, 'data': user})
    return jsonify({'message': 'invalid input', 'code': -2, 'data': updateAccount.errors})

@bp.route("/upload-password", methods=["POST"])
@jwt_required()
def update_password():
    updatePassword = UpdatePassword(meta={'csrf': False})

    if updatePassword.validate():
        user, _, msg = UserDataService().update_password(current_user.id, updatePassword.password.data)

        if user is None:
            return jsonify({'message': 'Cập nhật tài khoản không thành công', 'code': -1, 'data': None})
        return jsonify({'message': 'Cập nhật tài khoản thành công', 'code': 0, 'data': user})
    return jsonify({'message': 'invalid input', 'code': -2, 'data': updatePassword.errors})

@bp.route("/upload-count-download", methods=["POST"])
@jwt_required()
def update_download():
    data = request.json

    user, _, msg = UserDataService().update_download(current_user.id, data["number_download"], data["week_reset"])
    if user is None:
        return jsonify({'message': 'Cập nhật tài khoản không thành công', 'code': -1, 'data': None})
    return jsonify({'message': 'Cập nhật tài khoản thành công', 'code': 0, 'data': user})

@bp.route("/quan-ly-tai-lieu", methods=["GET"])
def manager_document():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    type = request.args.get("type", "all", type=str)
    return render_template('user/manager_doc.html', title='User',form=register, formlogin=login, formresetpw=resetpw, type=type)

@bp.route("/<account_id>-trang-ca-nhan")
def get_view_user(account_id):
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    page = request.args.get('page', 1, type=int)
    type = request.args.get('type', "all", type=str)

    user, _, _ = UserDataService().get_by_id_tuple(account_id)
    documents, _, _ = DocumentsDataService().get_by_account_id_with_paginate(account_id, page, type, "")

    return render_template('user/profile_view_user.html',form=register, formlogin=login, account_id=account_id, type=type, 
                           formresetpw=resetpw, documents=documents, user=user)

@bp.route("/search/<account_id>-trang-ca-nhan")
def search_view_user(account_id):
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', "", type=str)

    user, _, _ = UserDataService().get_by_id_tuple(account_id)
    documents, _, _ = DocumentsDataService().get_by_account_id_with_paginate(account_id, page, "all", keyword)

    return render_template('user/profile_view_search_user.html',form=register, formlogin=login, account_id=account_id, keyword=keyword, 
                           formresetpw=resetpw, documents=documents, user=user)

@bp.route("/quan-ly-tai-chinh")
def manager_financy():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    return render_template('user/manager_financy.html',form=register, formlogin=login, formresetpw=resetpw)

@bp.route("/tong-quan")
def overview():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    return render_template('user/overview.html',form=register, formlogin=login, formresetpw=resetpw)

@bp.route("/transactions")
@jwt_required()
def get_transactions():
    page = request.args.get('page', 1, type=int)

    transactions, code, msg = TransactionDataService().get_by_account_id_with_paginate(current_user.id, page, 20)

    return jsonify({"message": msg, "code": code, "data": transactions})

@bp.route("/stats")
@jwt_required()
def get_stats():
    year = request.args.get('year', datetime.now().year, type=int)
    transactions, code, msg = TransactionDataService().get_month_stats(current_user.id, year)

    return jsonify({"message": msg, "code": code, "data": transactions})

@bp.route("/stats-document")
@jwt_required()
def get_stats_document():
    year = request.args.get('year', datetime.now().year, type=int)
    documents, code, msg = DocumentsDataService().get_month_stats_document(current_user.id, year)

    return jsonify({"message": msg, "code": code, "data": documents})

@bp.route("/stats-view-document")
@jwt_required()
def get_stats_view_document():
    documents, code, msg = DocumentsDataService().get_month_stats_view_document(current_user.id)

    return jsonify({"message": msg, "code": code, "data": documents})

@bp.route("/stats-download-document")
@jwt_required()
def get_stats_download_document():
    documents, code, msg = DocumentsDataService().get_month_stats_download_document(current_user.id)

    return jsonify({"message": msg, "code": code, "data": documents})

@bp.route("/total")
@jwt_required()
def get_total():
    total_deposits, _, _ = TransactionDataService().get_total(current_user.id, "Nạp tiền")
    total_revenue, code, msg = TransactionDataService().get_total(current_user.id, "Bán tài liệu")

    return jsonify({"message": msg, "code": code, "data": {"total_deposits": total_deposits, "total_revenue": total_revenue}})