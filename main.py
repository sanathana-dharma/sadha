import os
import logging
from flask import Flask, redirect, request, url_for, make_response
from flask_login import (
    LoginManager,
    current_user
)
from _private import keys
import requests

# Internal imports
from user import User
import config
import treemgr
import auth
import utils
from utils import render_html


# =========================================================================
# Flask app setup
app = Flask(__name__, template_folder="static/templates/")
app.config.from_object(config)
app.secret_key = keys.SECRET_KEY
app.debug = True
app.testing = False
if not app.testing:
    logging.basicConfig(level=logging.INFO)

# Register the blueprint.
from treemgr.routes import mod
app.register_blueprint(treemgr.routes.mod, url_prefix='/admin')

from auth.routes import mod2
app.register_blueprint(auth.routes.mod2, url_prefix='/auth')


# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)
# Flask-Login helper to retrieve the current user from db
@login_manager.user_loader
def load_user(user_id):
	try:
		return User.get(user_id)
	except:
		return None

@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403

# =========================================================================
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

# Site main entry point
@app.route("/")
def index():
	return utils.redirect_admin_only()


@app.route("/search")
def search():
	di = {}
	return render_html("search.html", di)


# =========================================================================
# API (for future)
@app.route("/api/v2/test_response")
def users():
    headers = {"Content-Type": "application/json"}
    return make_response('Test worked!',
                         200,
                         headers=headers)


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
