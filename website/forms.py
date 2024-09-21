from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, FileField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Description')
    photo = FileField('Photo')
    discount = FloatField('Discount', validators=[DataRequired()])