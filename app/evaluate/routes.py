from flask import jsonify, render_template, request, redirect
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.evaluate.services import EvaluateDataService
from app.evaluate import bp

@bp.route("", methods=["POST"])
@jwt_required()
def create(document_id):
    type = request.args.get("type")
    evaluate, code, msg = EvaluateDataService().create_or_delete(document_id, current_user.id, type)

    return jsonify({'message': msg, 'code': code, 'data': evaluate})

@bp.route("", methods=["GET"])
@jwt_required()
def get(document_id):
    evaluate, code, msg = EvaluateDataService().get(document_id, current_user.id)
    return jsonify({'message': msg, 'code': code, 'data': evaluate})