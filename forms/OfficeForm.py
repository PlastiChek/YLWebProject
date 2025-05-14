from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


class OfficeForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[DataRequired()])
    name = StringField('Ваше имя', validators=[DataRequired()])
    email = StringField('Ваша почта', validators=[DataRequired()])
    telegram_id = StringField('Ваш telegram_id', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])