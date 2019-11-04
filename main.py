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
import contentmgr
import search
import auth
import utils
from utils import render_html

#Search related imports
from _private import keys
import requests
from algoliasearch.search_client import SearchClient


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='[[',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string=']]',
    ))



# =========================================================================
# Flask app setup
# Below line replaces  "app = Flask(__name__)"
app = CustomFlask(__name__, template_folder='static/templates')


app.config.from_object(config)
app.secret_key = keys.SECRET_KEY
app.debug = True
app.testing = False
if not app.testing:
    logging.basicConfig(level=logging.INFO)

# Register the blueprint.
from treemgr.routes import mod
app.register_blueprint(treemgr.routes.mod, url_prefix='/admin/treemgr')

from auth.routes import mod2
app.register_blueprint(auth.routes.mod2, url_prefix='/auth')

from contentmgr.routes import mod3
app.register_blueprint(contentmgr.routes.mod3, url_prefix='/admin/contentmgr')

from search.routes import mod4
app.register_blueprint(search.routes.mod4, url_prefix='/admin/search')

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
#Force SSL for all ursl across the site
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

@app.route("/admin")
def admin():
	return redirect("/admin/treemgr/list")

@app.route("/admin/search")
def searchtest():
	di = {}
	return render_html("search2.html", di)


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
