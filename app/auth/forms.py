from flask_wtf import FlaskForm as Form
from flask_login import current_user
from ..models import User
from wtforms import ValidationError, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class LoginForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我的登陆状态')
    submit = SubmitField('登陆')


class ResetPasswordForm(Form):
    password = PasswordField('输入新的密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码不一致。')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('更改')


class ResetPasswordEmailForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('发送')


class ChangePasswordForm(Form):
    old_password = PasswordField('输入原来密码', validators=[DataRequired()])
    password = PasswordField('输入新的密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码不一致。')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('更改')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('密码错误请重新输入。')

    def validate_password(self, field):
        if current_user.verify_password(field.data):
            raise ValidationError('新密码不能与当前密码一样。')


class ChangeEmailForm(Form):
    email = StringField('新的邮箱地址', validators=[DataRequired(), Length(1, 64), Email() ])
    submit = SubmitField('发送')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被使用。')


class RegistrationForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email() ])
    username = StringField('昵称', validators=[DataRequired(), Length(1, 64),
                                             Regexp('^[\u4e00-\u9fa5A-Za-z][\u4e00-\u9fa5A-Za-z0-9_.]*$',
                                             0,
                                             'Usernames must have only letters, '
                                             'numbers, dots or underscrores.')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码不一致。')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被使用。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该昵称已被使用。')



