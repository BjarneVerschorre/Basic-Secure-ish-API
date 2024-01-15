import os
from flask import Flask, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY','')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

from flask_wtf import CSRFProtect 
csrf = CSRFProtect(app)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per hour"],
    storage_uri="memory://",
)

from basic_api.routes.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from basic_api.routes.root import root_bp
app.register_blueprint(root_bp)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    flash("Rate limit exceeded. Please try again later.", "error")
    return redirect(url_for("/.home"))

@app.after_request
def after_request(response):
    # Disable caching to prevent people who are logged out pressing the back button and seeing their data
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response