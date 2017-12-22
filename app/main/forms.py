from flask_wtf import FlaskForm as Form
from flask_pagedown.fields import PageDownField
from wtforms import ValidationError, StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import User, Role


class NameForm(Form):
    name = StringField('What`s your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('城市', validators=[Length(0, 64)])
    about_me = TextAreaField('简介')
    submit = SubmitField('确定')


class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('账号', validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[\u4e00-\u9fa5A-Za-z][\u4e00-\u9fa5A-Za-z0-9_.]*$',
                                               0,
                                               'Usernames must have only letters,'
                                               'numbers, dots or underscrores.')])
    confirmed = BooleanField('验证')
    role = SelectField('角色', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('城市', validators=[Length(0, 64)])
    about_me = TextAreaField('简介')
    submit = SubmitField('确定')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() and field.data != self.user.email:
            raise ValidationError('该邮箱已被使用。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() and field.data != self.user.username:
            raise ValidationError('该账号已被使用。')


class PostForm(Form):
    body = PageDownField('内容', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(Form):
    body = StringField('评论', validators=[DataRequired()])
    submit = SubmitField('提交')







