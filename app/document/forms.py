from flask_wtf import FlaskForm
from wtforms import FieldList, Form, StringField, FormField, ValidationError, FileField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from app.model.models import Documents

class UploadDocumentForm(FlaskForm):
    old_name = StringField(validators=[DataRequired()])
    document_name = StringField(validators=[DataRequired("Tên tài liệu không được để trống")])
    description = StringField(validators=[DataRequired("Mô tả không được để trống"), Length(min=200)])
    type = StringField(validators=[DataRequired()])
    price = StringField(validators=[DataRequired("Giá bán tài liệu không được để trống")])
    categories = FieldList(StringField(validators=[DataRequired("Danh mục không được để trống")]))
    image = FileField()
    license = StringField(validators=[DataRequired("Giấy phép của tài liệu không được để trống")])

    def validate_document_name(self, document_name):
        document = Documents.find_by_name(document_name.data)
        if document != None:
            raise ValidationError("Đã có tài liệu có tên " + document_name.data)
        
    def validate_license(self, license):
        if license.data is None or license.data == "null":
            raise ValidationError("Giấy phép của tài liệu không được bỏ trống")
        
class UpdateDocumentForm(FlaskForm):
    document_id = IntegerField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired("Mô tả không được để trống"), Length(min=200)])
    price = StringField(validators=[DataRequired("Giá bán tài liệu không được để trống")])
    categories = FieldList(StringField(validators=[DataRequired("Danh mục không được để trống")]))
    image = FileField()
    license = StringField(validators=[DataRequired("Giấy phép của tài liệu không được để trống")])

    def validate_license(self, license):
        if license.data is None or license.data == "null":
            raise ValidationError("Giấy phép của tài liệu không được bỏ trống")
