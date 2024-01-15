from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class KeyGenForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Regexp('^[a-zA-Z0-9_]{3,25}$', message='Key name must be alphanumeric and between 3 and 25 characters long')
    ])
    submit = SubmitField('Get API Key')
