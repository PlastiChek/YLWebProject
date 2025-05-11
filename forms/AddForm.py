from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    price = StringField('Цена', validators=[DataRequired()])
    provider = StringField('Поставщик', validators=[DataRequired()])
    type = StringField('Тип товара', validators=[DataRequired()])
    submit = SubmitField('Добавить')