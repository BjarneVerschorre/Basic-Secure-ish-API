from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Regexp, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Regexp('^[a-zA-Z0-9]{3,15}$', message='Username must be alphanumeric and between 3 and 15 characters long')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
        ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
