import hashlib
import hmac
import json
import uuid
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests
from app.model.models import User
from app.momo.email import send_email_field
from app.momo import bp

@bp.route("/sendmail/<int:id>", methods=["POST"])
def guiMail(id):
    if id:
        user = User.find_by_id(id)
        send_email_field(user)

    return ''

@bp.route("/callMoMo", methods=["POST"])
@jwt_required()
def momo():
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    orderInfo = "Nap tien vao tai khoan"
    partnerCode = "MOMO"
    redirectUrl = request.json.get("redirectUrl")

    user_id = get_jwt_identity()
    ipnUrl = "http://174.129.69.18/momo/sendmail/" + str(user_id)
    
    amount = request.json.get("amount")
    orderId = str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    extraData = "" 
    partnerName = "MoMo Payment"
    requestType = "payWithMethod"
    storeId = "Test Store"
    orderGroupId = ""
    autoCapture = True
    lang = "vi"
    orderGroupId = ""

    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId \
                + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl\
                + "&requestId=" + requestId + "&requestType=" + requestType

    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'orderId': orderId,
        'partnerName': partnerName,
        'storeId': storeId,
        'ipnUrl': ipnUrl,
        'amount': amount,
        'lang': lang,
        'requestType': requestType,
        'redirectUrl': redirectUrl,
        'autoCapture': autoCapture,
        'orderInfo': orderInfo,
        'requestId': requestId,
        'extraData': extraData,
        'signature': signature,
        'orderGroupId': orderGroupId
    }

    data = json.dumps(data)

    clen = len(data)
    response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

    return {'message': 'thành công', 'code': 0, 'data': response.json()['payUrl']}
