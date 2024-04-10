from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from app.model.models import Categories

class EditCategoryForm(FlaskForm):
    id = IntegerField()
    name = StringField(label="Tên danh mục", validators=[DataRequired("Tên danh mục không thể thiếu")])
    description = StringField(label="Mô tả")
    parent_id = StringField(label="Danh mục cha")

    def validate_name(self, name):
        category = Categories.find_by_name(name.data)
        if category != None and int(self.id) != category.id:
            raise ValidationError("Đã có danh mục tên " + name.data)

class CreateCategoryForm(FlaskForm):
    name = StringField(label="Tên danh mục", validators=[DataRequired("Tên danh mục không thể thiếu")])
    description = StringField(label="Mô tả")
    parent_id = StringField(label="Danh mục cha")

    def validate_name(self, name):
        category = Categories.find_by_name(name.data)
        if category != None:
            raise ValidationError("Đã có danh mục tên " + name.data)
        
class EditDocumentForm(FlaskForm):
    status = BooleanField(label="Trạng thái")
    deletion_reason = StringField(label="Lý do xóa")

    def validate_deletion_reason(self, deletion_reason):
        if self.status.data == False and (deletion_reason.data == "" or deletion_reason.data is None):
            raise ValidationError("Chưa điền lý do xóa")