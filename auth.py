import json
import os
import logging
from flask import Flask, redirect, request, url_for, make_response
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from _private import keys
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from user import User
from main import app, login_manager

# =========================================================================
# OAuth2 client setup
client = WebApplicationClient(keys.GOOGLE_CLIENT_ID)

@app.route("/login")
def login():
	google_provider_cfg = get_google_provider_cfg()
	authorization_endpoint = google_provider_cfg["authorization_endpoint"]
	request_uri = client.prepare_request_uri(
	    authorization_endpoint,
	    redirect_uri=request.base_url + "/callback",
	    scope=["openid", "email", "profile"],
	)
	return redirect(request_uri)


@app.route("/login/callback")
def callback():
	code = request.args.get("code")
	google_provider_cfg = get_google_provider_cfg()
	token_endpoint = google_provider_cfg["token_endpoint"]
	token_url, headers, body = client.prepare_token_request(
	    token_endpoint,
	    authorization_response=request.url,
	    redirect_url=request.base_url,
	    code=code,
	)
	token_response = requests.post(
	    token_url,
	    headers=headers,
	    data=body,
	    auth=(keys.GOOGLE_CLIENT_ID, keys.GOOGLE_CLIENT_SECRET),
	)
	client.parse_request_body_response(json.dumps(token_response.json()))
	userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
	uri, headers, body = client.add_token(userinfo_endpoint)
	userinfo_response = requests.get(uri, headers=headers, data=body)

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
	#	pass

	# Begin user session by logging the user in
	login_user(user)

	# Send user back to homepage
	return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403

def get_google_provider_cfg():
    return requests.get(keys.GOOGLE_DISCOVERY_URL).json()
