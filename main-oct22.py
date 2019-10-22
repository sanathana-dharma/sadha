#main.py

import os
from flask import current_app, Flask, redirect, url_for, request
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
#import requests

import google.auth.transport.requests
import requests

from user import User

#Auth lib
import argparse
import treemgr
import config
import logging
import json
import utils
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
client = WebApplicationClient(config.GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


app.config.from_object(config)
app.debug = False
app.testing = False

# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)

# Register the blueprint.
from treemgr.routes import mod
app.register_blueprint(treemgr.routes.mod, url_prefix='/admin')


@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

def get_google_provider_cfg():
	print(json.dumps(config.GOOGLE_DISCOVERY_URL))
	return json.dumps(config.GOOGLE_DISCOVERY_URL)
    #return requests.get(config.GOOGLE_DISCOVERY_URL).json()

@app.route('/login', methods=['GET','POST'])
def login():
    # Find out what URL to hit for Google login
	#google_provider_cfg = get_google_provider_cfg()
	#authorization_endpoint = google_provider_cfg["authorization_endpoint"]
	authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
	# Use library to construct the request for login and provide
	# scopes that let you retrieve user's profile from Google
	request_uri = client.prepare_request_uri(
	    authorization_endpoint,
	    redirect_uri=request.base_url + "/callback",
	    scope=["openid", "email", "profile"],
	)
	return redirect(request_uri)


@app.route("/login/callback", methods=['GET'])
def callback():
    # Get authorization code Google sent back to you
	#req = google.auth.transport.requests.Request()

	code = request.args.get("code")
	print("code=")
	print(code)
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
	#google_provider_cfg = get_google_provider_cfg()
	#token_endpoint = google_provider_cfg["token_endpoint"]
	token_endpoint = "https://oauth2.googleapis.com/token"

    # Prepare and send request to get tokens! Yay tokens!
	token_url, headers, body = client.prepare_token_request(
	    token_endpoint,
	    authorization_response=request.url,
	    redirect_url=request.base_url,
	    code=code,
	)
	print("request object=")
	print(request)

	token_response = request.get(
	    token_url,
	    headers=headers,
	    data=body,
	    auth=(config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET),
	)

	# Parse the tokens!
	client.parse_request_body_response(json.dumps(token_response.json()))

	# Now that we have tokens (yay) let's find and hit URL
	# from Google that gives you user's profile information,
	# including their Google Profile Image and Email
	userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
	uri, headers, body = client.add_token(userinfo_endpoint)
	userinfo_response = requests.get(uri, headers=headers, data=body)

	# We want to make sure their email is verified.
	# The user authenticated with Google, authorized our
	# app, and now we've verified their email through Google!
	if userinfo_response.json().get("email_verified"):
	    unique_id = userinfo_response.json()["sub"]
	    users_email = userinfo_response.json()["email"]
	    picture = userinfo_response.json()["picture"]
	    users_name = userinfo_response.json()["given_name"]
	else:
	    return "User email not available or not verified by Google.", 400

	# Create a user in our db with the information provided
	# by Google
	user = User(
	    id_=unique_id, name=users_name, email=users_email, profile_pic=picture
	)

	# Doesn't exist? Add to database
	if not User.get(unique_id):
	    User.create(unique_id, users_name, users_email, picture)

	# Begin user session by logging the user in
	login_user(user)

	# Send user back to homepage
	return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
	logout_user()
	#return redirect(url_for("index"))
	return redirect(request_uri+'&prompt=consent')


#def get_google_provider_cfg():
#	print(json.dumps(config.GOOGLE_DISCOVERY_URL))
#    return json.dumps(config.GOOGLE_DISCOVERY_URL)

#https://stackoverflow.com/questions/51006382/no-module-named-requests-when-trying-to-use-google-oauth2-with-docker

#Add a default root route.
#@app.route("/login")
#def login():
#    return render_html("login.html")

#Add a default root route.
#@app.route("/home")
#@login_required
#def home():
#    return render_html("home.html")


@app.route("/dologin", methods=['GET'])
def dologin():
# (Receive token by HTTPS POST)
# ...
	token = request.form['idtoken']
	try:
	    # Specify the CLIENT_ID of the app that accesses the backend:
		idinfo = id_token.verify_oauth2_token(token, requests.Request(), config.GOOGLE_CLIENT_ID)

	    # Or, if multiple clients access the backend server:
	    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
	    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
	    #     raise ValueError('Could not verify audience.')

		if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
			raise ValueError('Wrong issuer.')

	    # If auth request is from a G Suite domain:
	    # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
	    #     raise ValueError('Wrong hosted domain.')

	    # ID token is valid. Get the user's Google Account ID from the decoded token.
		userid = idinfo['sub']
		#redirect(url_for('treemgr.list'))
		#return "/admin/dashboard"
		return redirect("/dashboard")
		#return "ID Valid!"
	except ValueError:
		# Invalid token
		pass

@app.route("/dologout",methods=['GET'])
def dologout():
	return redirect("https://appengine.google.com/_ah/logout?continue=http://www.google.com")



# Add an error handler. This is useful for debugging the live application,
# however, you should disable the output of the exception for production
# applications.
@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# This is only used when running locally. When running live, gunicorn runs
# the application.
#if __name__ == '__main__':
#	app.run(host='127.0.0.1', port=8080, debug=True)

if __name__ == "__main__":
    app.run(ssl_context="adhoc")
