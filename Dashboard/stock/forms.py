from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms.fields.core import DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from stock.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    mobileno = StringField('Mobile No.',
                        validators=[DataRequired(), Length( max=10)])
    adharno = StringField('Adhar No.',
                        validators=[DataRequired(), Length( max=12)])
    panno = StringField('Pan No.',
                        validators=[DataRequired(), Length( max=10)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_username(self, mobileno):
        if mobileno.data != current_user.mobileno:
            user = User.query.filter_by(mobileno=mobileno.data).first()
            if user:
                raise ValidationError('This No. is used by other user, Please give differnet one.')


class GetCurrentPriceForm(FlaskForm):
    stock_symbol = StringField('Stock Symbol',
                           validators=[DataRequired(), Length(min=2, max=200)])
    number_of_shares= IntegerField('No. of Shares',
                           validators=[DataRequired()])
    submit = SubmitField('Get Current Price')
    


class WatchStockForm(FlaskForm):
    stock_symbol = StringField('Stock Symbol', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Add')