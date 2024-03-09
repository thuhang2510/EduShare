import os
from flask_wtf import FlaskForm
from wtforms import FieldList, Form, StringField, FormField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from app.model.models import Documents

class UploadDocumentForm(FlaskForm):
    old_name = StringField(validators=[DataRequired()])
    document_name = StringField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired(), Length(min=200)])
    type = StringField(validators=[DataRequired()])
    price = StringField(validators=[DataRequired()])
    categories = FieldList(StringField(validators=[DataRequired()]))

    def validate_document_name(self, document_name):
        document = Documents.find_by_name(document_name.data)
        if document != None:
            raise ValidationError("Đã có tài liệu có tên " + document_name.data)
