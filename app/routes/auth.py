import logging
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user
from app import db
from app.models import User
from app.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logging.info('User is already authenticated, redirecting to main.index')
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            logging.info('Login successful, redirecting to main.index')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
            logging.info('Invalid login attempt')
    logging.info('Rendering login.html template')
    return render_template('login.html', form=form)