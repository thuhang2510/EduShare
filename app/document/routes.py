import os
from flask import jsonify, render_template, request, redirect
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.document import bp
from app.document.forms import UploadDocumentForm
from app.document.services import DocumentsDataService
from constant import DocumentS3
from s3_helper import upload
from app.extensions import uploader_permission

@bp.route("/upload", methods=["GET"])
def index():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})
    return render_template('document/upload_doc.html', title='Document',form=register, formlogin=login, formresetpw=resetpw)
    
@bp.route("/upload-multi", methods=['POST'])
@jwt_required()
@uploader_permission.require(http_exception=403)
def upload_multi():
    files = request.files.getlist("file") 

    for f in files: 
        file_path = f"upload_files/{f.filename}"
        if os.path.exists(file_path):
            return jsonify({'message': f'Tài liệu {f.filename} đã có trong tạm thời', 'code': -1, 'data': None})
        
        f.save(os.path.join(DocumentS3.UPLOAD_FOLDER, f.filename))
        
    return jsonify({'message': 'Tài liệu lưu vào tạm thời thành công', 'code': 0, 'data': None})
    
@bp.route("/delete-wait-file", methods=['DELETE'])
@jwt_required()
def delete_file_wait():
    fileName = request.args.get("fileName")     
    
    file_path = f"upload_files/{fileName}"
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'Xóa tài liệu chờ thành công', 'code': 0, 'data': None})
    
    return jsonify({'message': 'Xóa tài liệu chờ thất bại', 'code': -1, 'data': None})
    
@bp.route("/check-file", methods=['GET'])
@jwt_required()
@uploader_permission.require(http_exception=403)
def check_file_exist():
    fileName = request.args.get("fileName")

    file_path = f"upload_files/{fileName}"
    if os.path.exists(file_path):
        return jsonify({'message': f'Tài liệu {fileName} đã có trong tạm thời', 'code': -1, 'data': None})
        
    return jsonify({'message': f'Tài liệu {fileName} chưa có trong tạm thời', 'code': 0, 'data': None})
    
@bp.route("/upload-s3", methods=['POST'])
@jwt_required()
@uploader_permission.require(http_exception=403)
def upload_s3():
    uploadDocument = UploadDocumentForm(meta={'csrf': False})

    for entry in request.json.get('categories'):
        uploadDocument.categories.append_entry(entry)

    if uploadDocument.validate():
        document, _, msg = DocumentsDataService().create(current_user.id, uploadDocument.data)

        if document is not None:
            upload(f"upload_files/{uploadDocument.old_name.data}", DocumentS3.BUCKET, uploadDocument.document_name.data)
            return jsonify({'message': 'Tải tài liệu lên thành công', 'code': 0, 'data': None})
        else:
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'invalid input', 'code': -2, 'data': uploadDocument.errors})
        