from datetime import datetime
import os
from flask import jsonify, render_template, request, redirect, json, send_file, send_from_directory
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.ai import tasks
from app.document import tasks as document_tasks
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.document import bp
from app.document.email import send_report
from app.document.forms import UpdateDocumentForm, UploadDocumentForm
from app.document.services import DocumentsDataService
from app.auth.services import UserDataService
from constant import DocumentS3
from ultil import file_helper
from ultil.custom_random import generate_random_string
from ultil.s3_helper import download, upload
from app.extensions import uploader_permission, downloader_permission, reporter_permission, editter_permision

import aspose.words as aw

PATH = "app/static/images/"

@bp.app_template_filter()
def numberFormat(value):
    return format(int(value), ',d')

@bp.app_template_filter()
def get_only_document_name(document_name):
    return document_name.rsplit(".", 1)[0]

@bp.app_template_filter()
def format_datetime(datetime):
    return datetime.strftime('%d-%m-%Y %H:%M:%S')

@bp.app_template_filter()
def count_evaluate(values):
    like = 0
    dislike = 0

    for value in values:
        if(value.type == 'like'):
            like += 1
        elif (value.type == 'dislike'):
            dislike += 1

    if(like + dislike == 0):
        return 0

    result = like / (like + dislike) * 100

    if (result.is_integer()):
        return int(result)
    
    return "{:.2f}".format(result) 

@bp.app_template_filter()
def format_datetime(date):
    return date.strftime("%d/%m/%Y %H:%M:%S")

@bp.app_template_filter()
def component_license(license_string):
    return [component.strip().lower() for component in license_string.split(" ")]

@bp.route("/upload", methods=["GET"])
def index():
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})
    return render_template('document/upload_doc.html', title='Tải tài liệu lên',form=register, formlogin=login, formresetpw=resetpw)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/upload-multi", methods=['POST'])
@jwt_required()
@uploader_permission.require(http_exception=403)
def upload_multi():
    files = request.files.getlist("file") 

    for f in files: 
        file_path = f"upload_files/{f.filename}"
        if os.path.exists(file_path):
            return jsonify({'message': f'Tài liệu {f.filename} đã có trong tạm thời', 'code': -1, 'data': None})
        
        if (allowed_file(f.filename) is False):
            return jsonify({'message': f'Tài liệu {f.filename} không đúng định dạng được phép tải lên', 'code': -1, 'data': None})

        f.save(file_path)
        f.close()

        if f.content_type != 'application/pdf':
            file_helper.convert_doc_to_pdf(f"upload_files/{f.filename}", f"upload_files/{f.filename.replace('docx', 'pdf')}")
        
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
    imgs = request.files.getlist("image")
    fileName = ""

    for f in imgs: 
        fileName = f"anh{generate_random_string(8)}.{f.filename.split('.')[-1]}"
        path_img = os.path.join(PATH, fileName)
        f.save(path_img)
        f.close()

    uploadDocument = UploadDocumentForm(meta={'csrf': False})
    _categories = json.loads(request.form.get('categories'))["categories"]
    for entry in _categories:
        uploadDocument.categories.append_entry(entry)

    if uploadDocument.validate():        
        document, _, msg = DocumentsDataService().create(current_user.id, uploadDocument.data, "/static/images/" + fileName)

        if document is not None:
            upload(f"upload_files/{uploadDocument.old_name.data}", DocumentS3.BUCKET, uploadDocument.document_name.data)

            url = f"https://edushare-s3.s3.amazonaws.com/{document.document_name}"
            tasks.page_pdf_and_build_vector_db.delay(url, document.document_name, document.id, current_user.id)
            document_tasks.delete_wait_file.delay(uploadDocument.old_name.data)

            return jsonify({'message': 'Tải tài liệu lên thành công', 'code': 0, 'data': None})
        else:
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'invalid input', 'code': -2, 'data': uploadDocument.errors})

@bp.route("/get_all_new", methods=['GET'])
def get_documents_new():
    limit = None

    if 'limit' in request.args:
        limit = request.args.get("limit")

    document, _, msg = DocumentsDataService().get_all_new(limit)

    if document is not None:
        return jsonify({'message': 'Tải tài liệu lên thành công', 'code': 0, 'data': document})
    else:
        return jsonify({'message': msg, 'code': -1, 'data': None})

@bp.route("/get_all_saved", methods=['GET'])
@jwt_required()
def get_documents_saved():
    limit = None

    if 'limit' in request.args:
        limit = request.args.get("limit")

    document, _, msg = DocumentsDataService().get_all_saved(current_user.id, limit)

    if document is not None:
        return jsonify({'message': 'Tải tài liệu lên thành công', 'code': 0, 'data': document})
    else:
        return jsonify({'message': msg, 'code': -1, 'data': None})
    
@bp.route("/get_all_view", methods=['GET'])
def get_documents_view():
    limit = None

    if 'limit' in request.args:
        limit = request.args.get("limit")

    document, _, msg = DocumentsDataService().get_all_view(limit)

    if document is not None:
        return jsonify({'message': 'Tải tài liệu lên thành công', 'code': 0, 'data': document})
    else:
        return jsonify({'message': msg, 'code': -1, 'data': None})
    
@bp.route("/<int:id>", methods=['GET'])
def get_document_form(id):
    register = RegisterForm(meta={'csrf': False})
    login = LoginForm(meta={'csrf': False})
    resetpw = ResetPasswordRequestForm(meta={'csrf': False})

    DocumentsDataService().update_view(id)
    document, _, _ = DocumentsDataService().get_by_id(id)

    if(document is not None):
        document["document_name"] = document["document_name"].split(".")[0]
        
        like, dislike, save = DocumentsDataService().count_evaluate(document)
        document["like"] = like
        document["save"] = save
        document["dislike"] = dislike

    return render_template('document/document_detail.html', title="" + document["document_name"], form=register, formlogin=login, 
                        formresetpw=resetpw, document=document)

@bp.route("/<int:id>/detail", methods=['GET'])
@jwt_required()
def get_document_detail(id):
    document, _, msg = DocumentsDataService().get_by_purchase(id, current_user.id)

    if document is not None:
        document["document_name"] = document["document_name"].split(".")[0]

        return jsonify({'message': 'Lấy tài liệu lên thành công', 'code': 0, 'data': document})
    else:
        return jsonify({'message': msg, 'code': -1, 'data': None})
    
@bp.route("/category", methods=["GET"])
def get_documents_by_category():
    category_name = request.args.get('category_name')
    categories, _, msg = DocumentsDataService().get_by_category(category_name, limit=5)

    if categories is None:
        return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'Lấy danh mục thành công', 'code': 0, 'data': categories})

@bp.route("/<int:id>/download", methods=["GET"])
@jwt_required()
@downloader_permission.require(http_exception=403)
def download_document(id):
    document, code, msg = DocumentsDataService().update_download(id)

    if not document:
        return jsonify({'message': msg, 'code': -1, 'data': None})
    
    document_name = document["document_name"]
    download(document_name, DocumentS3.BUCKET)

    return send_file(f"./download_files/{document_name}", mimetype="application/pdf")

@bp.route("/<int:id>/download_premium", methods=["GET"])
@jwt_required()
@downloader_permission.require(http_exception=403)
def download_document_premium(id):
    if((current_user.premium != 0 and (datetime.now() - current_user.premium_start).days <= current_user.premium)):
        document, code, msg = DocumentsDataService().update_download(id)

        if not document:
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
        document_name = document["document_name"]
        download(document_name, DocumentS3.BUCKET)

        return send_file(f"./download_files/{document_name}", mimetype="application/pdf")
    
    return "no send", 403

@bp.route("/", methods=['GET'])
@jwt_required()
def get_all_document():
    page = request.args.get('page', 1, type=int)
    type = request.args.get('type', "all", type=str)

    document, _, msg = DocumentsDataService().get_by_account_id_with_paginate(current_user.id, page, 12, type, "")

    if document is not None:
        results = {
            "first": document.first,
            "has_next": document.has_next,
            "has_prev": document.has_prev,
            "last": document.last,
            "next_num": document.next_num,
            "page": document.page,
            "pages": document.pages,
            "prev_num": document.prev_num,
            "total": document.total
        }

        results["items"] = []

        for item in document.items:
            results["items"].append(item.to_dict_has_evaluate())
        return jsonify({'message': 'Lấy tài liệu thành công', 'code': 0, 'data': results})

    return jsonify({'message': msg, 'code': -1, 'data': None})

@bp.route("/processing", methods=['GET'])
@jwt_required()
def get_processing():
    page = request.args.get('page', 1, type=int)

    documents, _, msg = DocumentsDataService().get_processing_with_paginate(current_user.id, page, 12)

    if documents is not None:
        results = {
            "first": documents.first,
            "has_next": documents.has_next,
            "has_prev": documents.has_prev,
            "last": documents.last,
            "next_num": documents.next_num,
            "page": documents.page,
            "pages": documents.pages,
            "prev_num": documents.prev_num,
            "total": documents.total
        }

        results["items"] = []

        for item in documents.items:
            results["items"].append(item.to_dict_has_evaluate())
        return jsonify({'message': 'Lấy tài liệu thành công', 'code': 0, 'data': results})

    return jsonify({'message': msg, 'code': -1, 'data': None})

@bp.route("/process_fail", methods=['GET'])
@jwt_required()
def get_process_fail():
    page = request.args.get('page', 1, type=int)

    documents, _, msg = DocumentsDataService().get_process_fail_with_paginate(current_user.id, page, 12)

    if documents is not None:
        results = {
            "first": documents.first,
            "has_next": documents.has_next,
            "has_prev": documents.has_prev,
            "last": documents.last,
            "next_num": documents.next_num,
            "page": documents.page,
            "pages": documents.pages,
            "prev_num": documents.prev_num,
            "total": documents.total
        }

        results["items"] = []

        for item in documents.items:
            results["items"].append(item.to_dict_has_evaluate())
        return jsonify({'message': 'Lấy tài liệu thành công', 'code': 0, 'data': results})

    return jsonify({'message': msg, 'code': -1, 'data': None})

@bp.route("/<int:id>/show", methods=['GET'])
def get_by_id_tuple(id):
    document, _, msg = DocumentsDataService().get_by_id_tuple_with_categories(id)

    if document is not None:
        return jsonify({'message': 'Lấy tài liệu thành công', 'code': 0, 'data': document})

    return jsonify({'message': msg, 'code': -1, 'data': None})

@bp.route('/update_document', methods=['POST'])
@jwt_required()
@editter_permision.require(http_exception=403)
def update_document():
    imgs = request.files.getlist("image")
    fileName = ""

    for f in imgs: 
        fileName = f"anh{generate_random_string(8)}.{f.filename.split('.')[-1]}"
        path_img = os.path.join(PATH, fileName)
        f.save(path_img)
        f.close()

    updateDocument = UpdateDocumentForm(meta={'csrf': False})
    _categories = json.loads(request.form.get('categories'))["categories"]
    for entry in _categories:
        updateDocument.categories.append_entry(entry)

    if updateDocument.validate():        
        document, _, msg = DocumentsDataService().update_info(updateDocument.document_id.data, updateDocument.data, "/static/images/" + fileName)

        if document is not None:
            return jsonify({'message': 'Cập nhật tài liệu lên thành công', 'code': 0, 'data': document})
        else:
            return jsonify({'message': msg, 'code': -1, 'data': None})
        
    return jsonify({'message': 'invalid input', 'code': -2, 'data': updateDocument.errors})

@bp.route('/<document_id>/delete', methods=['DELETE'])
@jwt_required()
def delete(document_id):
    document, _, msg = DocumentsDataService().delete(document_id)

    if document is not None:
        return jsonify({'message': 'Xóa tài liệu lên thành công', 'code': 0, 'data': document})
    else:
        return jsonify({'message': msg, 'code': -1, 'data': None})
    
@bp.route('/<document_id>/report', methods=['POST'])
@jwt_required()
@reporter_permission.require(http_exception=403)
def report(document_id):
    files = request.files.getlist("file") 

    if (allowed_file(files[0].filename) is False):
        return jsonify({'message': f'Tài liệu {files[0].filename} không đúng định dạng được phép tải lên', 'code': -1, 'data': None})

    file_path = os.path.join("app/report_files", files[0].filename)
    files[0].save(file_path)

    document, _, _ = DocumentsDataService().get_by_id_with_account(document_id)
    user, _, _ = UserDataService().get_by_id(current_user.id)

    data, code, msg = send_report(document, user, "aedushare@gmail.com", request.form['content'], ('report_files/' + files[0].filename, "application/pdf"))
    os.remove(file_path)

    return jsonify({'message': msg, 'code': code, 'data': data})

@bp.route("/<document_id>/re_load", methods=['POST'])
@jwt_required()
def re_load(document_id):
    try:
        document, code, _ = DocumentsDataService().get_by_id(document_id)

        if(code != 0):
            return jsonify({'message': 'Tài liệu không tồn tại', 'code': 0, 'data': None}) 
        
        DocumentsDataService().update_processing_status(0, document["id"])
        url = f"https://edushare-s3.s3.amazonaws.com/{document['document_name']}"
        tasks.page_pdf_and_build_vector_db.delay(url, document['document_name'], document['id'], current_user.id)

        return jsonify({'message': 'Đang xử lý tài liệu', 'code': 0, 'data': None})    
    except Exception as e:
        return jsonify({'message': 'Không thể xử lý tài liệu', 'code': -1, 'data': None})       
        