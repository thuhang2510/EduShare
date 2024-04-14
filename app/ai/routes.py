from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.ai import bp
from app.ai.services import AIDataService

chat_history = {}  #cái này đang bị tất cả dùng chung 1 dict

@bp.route('/load_doc', methods=['POST'])
@jwt_required()
def load_pdf_and_build_vector_db():
    chat_history[current_user.id] = []
    document_edu_name = request.json.get("document_name")
    document_id = request.json.get("document_id")
    api_key = request.json.get("api_key")
    url = f"https://edushare-s3.s3.amazonaws.com/{document_edu_name}.pdf"

    data, code, msg = AIDataService().page_pdf_and_build_vector_db(url, document_edu_name, document_id, current_user.id, api_key)
    return jsonify({'message': msg, 'code': code, 'data': data})

@bp.route('/ask_ai', methods=['POST'])
@jwt_required()
def ask_ai():
    ask = request.json.get("ask")
    document_edu_name = request.json.get("document_name")
    document_id = request.json.get("document_id")
    api_key = request.json.get("api_key")
    
    data, code, msg = AIDataService().chat_with_ai(ask, chat_history[current_user.id], document_edu_name, document_id, current_user.id, api_key)
    return jsonify({'message': msg, 'code': code, 'data': data})

@bp.route('/thu', methods=['GET'])
def thu():
    return AIDataService().thu()