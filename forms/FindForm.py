from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FindForm(FlaskForm):
    find = StringField('Поиск', validators=[DataRequired()])
    submit = SubmitField('Поиск')