from flask import jsonify, render_template, request, redirect
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.purchase.services import PurchaseDataService
from app.purchase import bp

@bp.route("", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json()
    purchase, code, msg = PurchaseDataService().create(data["document_id"], data["account_id"], current_user.id, data["amount"])
    return jsonify({'message': msg, 'code': code, 'data': purchase})

@bp.route("", methods=["GET"])
@jwt_required()
def get():
    document_id = request.args.get("document_id")

    purchase, code, msg = PurchaseDataService().get(document_id, current_user.id)
    return jsonify({'message': msg, 'code': code, 'data': purchase})
    