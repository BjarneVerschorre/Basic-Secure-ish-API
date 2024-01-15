import os
import hashlib
import secrets
import uuid
from functools import wraps
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session

api_bp = Blueprint('api', __name__)
PEPPER = os.getenv('PEPPER', '')


def secure_equals(a:str, b:str) -> bool:
    '''Compare two strings in constant time to prevent timing attacks'''
    equal = len(a) == len(b)
    len_shortest = min(len(a), len(b))
    
    for i in range(len_shortest):
        if a[i] != b[i]:
            equal = False
            
    return equal


def hash_api_key(api_key: str, salt: str) -> str:
    ''' Hashes the API key with the salt and pepper using SHA256 '''
    return hashlib.sha256((api_key+salt+PEPPER).encode('utf-8')).hexdigest()


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from basic_api.models.api_keys import ApiKey

        api_auth_key = request.headers.get('Authorization')

        if not api_auth_key:
            return jsonify({'message': 'API key required'}), 401

        query_results = ApiKey.query.all()
        for entry in query_results:
            stored_api_key_hash = entry.api_key if entry else ''
            stored_salt = entry.salt if entry else ''

            hashed_api_key = hash_api_key(api_auth_key, stored_salt)

            if secure_equals(hashed_api_key, stored_api_key_hash):
                return f(*args, **kwargs)

        return jsonify({'message': 'Invalid API key'}), 401
    return decorated_function


@api_bp.route('/revoke/<key_id>', methods=['POST'])
def revoke(key_id):
    from basic_api.models.api_keys import ApiKey
    from basic_api.models.users import Users
    
    user = Users.query.filter_by(username=session.get('username')).first()
    if not user:
        flash('Something went wrong', 'error')
        return redirect(url_for('/.home'))
    
    api_key = ApiKey.query.filter_by(id=key_id, user_id=user.id).first()
    if not api_key:
        flash('Couldn\'t revoke API key', 'error')
        return redirect(url_for('/.home'))
    
    api_key.revoke()
    
    flash("API key revoked", "info")
    return redirect(url_for('/.dashboard'))

@api_bp.route('/generate-key', methods=['POST'])
def generate_api_key():    
    from basic_api.models.key_gen_form import KeyGenForm
    form = KeyGenForm()
    if 'username' not in session:
        flash('You must be logged in to generate an API Key', 'error')
        return redirect(url_for('/.home'))
    
    if not form.validate_on_submit():
        return render_template('dashboard.html', username=session['username'], form=form)
    
    from basic_api.models.api_keys import ApiKey
    from basic_api.models.users import Users

    user = Users.query.filter_by(username=session['username']).first()
    if not user:
        flash('Something went wrong', 'error')
        return redirect(url_for('/.home'))

    api_key = ApiKey.query.filter_by(user_id=user.id).first()

    if api_key:
        flash(f'You already have an API key', 'info')
        return redirect(url_for('/.dashboard'))
    
    from basic_api import db

    api_key_text = str(uuid.uuid4())
    key_name = form.name.data
    salt = secrets.token_hex(16)
    key_hash = hash_api_key(api_key_text, salt)

    api_key = ApiKey(key_name, key_hash, salt, user.id)
    user.api_key_rel.append(api_key)
    db.session.add(api_key)
    db.session.commit()

    flash(
        f'Your API Key: {api_key_text} (this will not show again)', 'success')
    return redirect(url_for('/.dashboard'))


@api_bp.route('/')
def hello():
    return render_template('api.html')


@api_bp.route('/sum', methods=['GET'])
@api_key_required
def sum():
    if 'a' not in request.args or 'b' not in request.args:
        return 'Invalid query parameters', 400

    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 0))

    result = a + b
    return jsonify({'result': result})
