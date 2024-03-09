import enum

class TransactionChoices(enum.Enum):
    RECHARGE = 'Nạp tiền'
    BUY_DOCUMENT = 'Mua tài liệu'
    RECEIVE_MONEY = 'Nhận tiền'

class DocumentS3:
    UPLOAD_FOLDER = 'upload_files'
    BUCKET = 'edushare-s3'