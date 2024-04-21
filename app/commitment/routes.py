from datetime import datetime
from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_login import current_user
from app.commitment import bp
from constant import DocumentS3
from ultil.pdf import create_pdf
from ultil.s3_helper import upload

@bp.route('/pdf', methods=['POST'])
@jwt_required()
def pdf():
    date = datetime.today().strftime('%d/%m/%Y')
    content = f"<h3 class='text-center mb-3'>Bản cam kết tự chịu trách nghiệm khi tải tài liệu lên</h3>\
                <p><strong>Tôi, {current_user.fullname}, xác nhận rằng tôi đã đọc và hiểu các điều khoản và điều kiện của trang web này, bao gồm cả chính sách bản quyền.</strong></p>\
                <p><strong>Tôi cam kết rằng tôi sẽ chỉ tải lên trang web này những tài liệu mà tôi có quyền tải lên.</strong>Tôi hiểu rằng tôi có thể bị truy tố về mặt pháp lý nếu tôi vi phạm luật bản quyền.</p>\
                <p><strong>Tôi cũng cam kết rằng tôi sẽ không tải lên trang web này bất kỳ tài liệu nào có nội dung bất hợp pháp, khiêu dâm, thù hận hoặc mang tính xúc phạm.</strong> Tôi hiểu rằng tôi có thể bị cấm truy cập vào trang web này nếu tôi vi phạm các điều khoản và điều kiện này.</p>\
                <p><strong>Tôi tự chịu trách nhiệm về tất cả các tài liệu mà tôi tải lên trang web này.</strong> Tôi hiểu rằng trang web này không chịu trách nhiệm về bất kỳ thiệt hại nào có thể phát sinh do việc tải lên tài liệu của tôi.</p>\
                <p><strong>Tôi đồng ý bồi thường cho trang web này cho bất kỳ thiệt hại nào phát sinh do việc tải lên tài liệu của tôi.</strong></p>\
                <p><strong>Bằng cách nhấp vào nút 'Đồng ý', tôi xác nhận rằng tôi đã đọc, hiểu và chấp nhận bản cam kết này.</strong></p>\
                <p><strong>Ngày: {date}</strong></p>\
                <p><strong>Chữ ký:</strong></p>\
                <p><strong>{current_user.fullname}</strong></p>"
    create_pdf(content)
    date = datetime.today().strftime('%d-%m-%Y')
    upload(f"commitment.pdf", DocumentS3.BUCKET, f"commitment/commitment-{current_user.fullname}-{date}.pdf")
    return jsonify({'message': 'Tải cam kết lên thành công', 'code': 0, 'data': None})
