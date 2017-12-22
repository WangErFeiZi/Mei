from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm, \
    ChangeEmailForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordEmailForm
from .. import db
from ..models import User
from ..email import send_email
from flask_login import login_required, login_user, logout_user, current_user
import hashlib


@auth.before_app_request
def before_request():
    if current_user.is_authenticated :
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('错误的用户名或者密码。')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功注销当前用户。')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '账号验证', 'auth/email/confirm', user=user, token=token)
        flash('成功注册！已经发送验证邮件。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '验证账号', 'auth/email/confirm', user=current_user, token=token)
    flash('已经重新发送验证邮件。')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
# @login_required
def confirm(token):
    # if current_user.is_authenticated:
    #     confirm_token, email, key = User.confirm(token)
    # else:
    user_id, email, key = User.confirm(token)
    user = User.query.filter_by(id=user_id).first()
    # if key is None and user_id != current_user.id:
    #     return redirect(url_for('main.index'))
    # elif
    if key == 'reset_password' and user is not None:
        return redirect(url_for('auth.reset_password_confirmed', token=token))
    elif key == 'change_email' and user is not None:
        user.email = email
        user.avatar_hash = hashlib.md5(user.email.encode('utf-8')).hexdigest()
        db.session.add(user)
        db.commit()
        flash('成功修改邮箱为{}！'.format(email))
    elif not current_user.is_authenticated and user is not None:
        flash('请先登录账号！')
    elif current_user.is_authenticated and current_user == user:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('成功验证账号！')
    elif user is None:
        return render_template('404.html'), 400
    else:
        flash('链接无效或过期。')
    return redirect(url_for('main.index'))


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = current_user.generate_confirmation_token(email=form.email.data, key='change_email')
        send_email(form.email.data, '验证账号', 'auth/email/confirm', user=current_user, token=token)
        flash('验证邮件已经发往{}。'.format(form.email.data))
        form.email.data = ''
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()
        flash('成功修改密码。')
    form.old_password.data = ''
    form.password.data = ''
    form.password2.data = ''
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_confirmed(token):
    # if not current_user.is_anonymous:
    if current_user.is_authenticated:
        flash('你已经登录了。')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=User.confirm(token)[0]).first()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('成功修改密码，请重新登录。')
    form.password.data = ''
    form.password2.data = ''
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token(email=form.email.data, key='reset_password')
        send_email(form.email.data, '验证账号', 'auth/email/confirm', user=user, token=token)
        flash('验证邮件已经发往{}。'.format(form.email.data))
        form.email.data = ''
    return render_template('auth/reset_password.html', form=form)


