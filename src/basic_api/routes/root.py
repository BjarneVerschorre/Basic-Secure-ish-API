import os
import secrets
from functools import wraps
from basic_api import db
from basic_api import limiter
from basic_api.models.users import Users
from basic_api.models.api_keys import ApiKey
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from argon2 import PasswordHasher, exceptions


PEPPER = os.getenv('PEPPER', '')
root_bp = Blueprint('/', __name__)


def logged_in_required(f):
    ''' Decorator to ensure that the user is logged in before accessing a page'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ('username' not in session) or (session.get('ip_address','') != request.remote_addr):
            flash('You must be logged in to view this page', 'error')
            return redirect(url_for('/.login'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_to_dashboard(f):
    ''' Decorator to redirect the user to the dashboard if they are already logged in'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return redirect(url_for('/.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@root_bp.route('/')
@redirect_to_dashboard
def home():
    from basic_api.models.login_form import LoginForm
    form = LoginForm()

    return render_template('home.html', form=form)


@root_bp.route('/login', methods=['POST', 'GET'])
@limiter.limit("5 per minute", error_message="Too many login attempts", methods=['POST'])
@redirect_to_dashboard
def login():
    from basic_api.models.login_form import LoginForm
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form=form)

    if not form.validate_on_submit():
        return render_template('login.html', form=form)

    username = form.username.data
    password = form.password.data
    
    if not username or not password:
        flash('Invalid username or password', 'error')
        return redirect(url_for('/.login'))

    user = Users.query.filter_by(username=username).first()
    stored_password = user.password if user else ''
    stored_salt = user.salt if user else ''

    if not user:
        flash('Invalid username or password', 'error')
        return redirect(url_for('/.login'))

    pw_hasher = PasswordHasher()

    try:
        pw_hasher.verify(
            stored_password, password + stored_salt + PEPPER)

        # No need for an if-statement since verify() will throw an exception if the password is incorrect
        session['username'] = username
        session['ip_address'] = request.remote_addr
        return redirect(url_for('/.dashboard'))

    except exceptions.VerifyMismatchError:
        flash('Invalid username or password', 'error')

    except: 
        flash('Something went wrong', 'error')

    return redirect(url_for('/.home'))


@root_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("1 per hour", error_message="Too many register attempts", methods=['POST'])
@redirect_to_dashboard
def register():
    from basic_api.models.register_form import RegisterForm
    form = RegisterForm()
    
    if request.method == 'GET':
        return render_template('register.html', form=form)

    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    username = form.username.data
    password = form.password.data
    
    if not username or not password:
        flash('Invalid username or password', 'error')
        return redirect(url_for('/.register'))

    user = Users.query.filter_by(username=username).first()
    if user:
        flash('Username already exists', 'error')
        return redirect(url_for('/.register'))

    pw_hasher = PasswordHasher()
    salt = secrets.token_hex(16)
    password_hash = pw_hasher.hash(password+salt+PEPPER)

    user = Users(username, password_hash, salt)

    db.session.add(user)
    db.session.commit()

    session['username'] = username
    return redirect(url_for('/.dashboard'))


@root_bp.route('/dashboard')
@logged_in_required
def dashboard():
    user = Users.query.filter_by(username=session['username']).first()
    if not user:
        flash('Something went wrong', 'error')
        return redirect(url_for('/.home'))

    api_keys = ApiKey.query.filter_by(user_id=user.id).all()
    from basic_api.models.key_gen_form import KeyGenForm
    form = KeyGenForm()

    return render_template('dashboard.html', username=session['username'], api_keys=api_keys, form=form)


@root_bp.route('/logout', methods=['POST'])
@logged_in_required
def logout():
    session.pop('username', None)
    
    flash('You have been logged out', 'info')
    return redirect(url_for('/.home'))
