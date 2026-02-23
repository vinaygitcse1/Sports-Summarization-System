from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])

class SummaryForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=200)])
    text = TextAreaField('Commentary Text', validators=[DataRequired(), Length(min=50)])
    max_length = IntegerField('Max Summary Length', default=150, validators=[Optional()])
    min_length = IntegerField('Min Summary Length', default=30, validators=[Optional()])