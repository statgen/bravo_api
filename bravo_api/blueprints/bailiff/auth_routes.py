"""@package Bailiff Routes
Provide authorization endpoints.
Provide login_manager.
"""
from flask import Blueprint, current_app, jsonify, url_for, request, redirect, session, abort
from flask_login import LoginManager, current_user, login_user, logout_user
import google_auth_oauthlib.flow
from oauth2client import client
from datetime import timedelta
import requests
import json
from .dummy_user_mgmt import DummyUserMgmt

login_manager = LoginManager()
bp = Blueprint('auth_routes', __name__)

def init_user_management(app, user_management=None):
    if user_management is None:
        user_management = DummyUserMgmt
    # Set user managment strategy on application
    app.user_mgmt = user_management()

    login_manager.user_loader(app.user_mgmt.load)
    login_manager.init_app(app)

def user_auth_status():
    return({'user': current_user.get_id(),
            'authenticated': current_user.is_authenticated,
            'active': current_user.is_active,
            'login_disabled': current_app.config.get('LOGIN_DISABLED')}
           )


@bp.route('/auth_status', methods=['GET', 'POST'])
def auth_status():
    return jsonify(user_auth_status())


@bp.route('/accessdenied')
@login_manager.unauthorized_handler
def access_denied():
    return "Access Denied"


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return jsonify(user_auth_status())


# End point for completing Authorization Code Flow w/ PKCE.
@bp.route('/auth_code', methods=['POST'])
def auth_code():
    # Get code from post data
    auth_code = request.json.get('code')

    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        current_app.config['GOOGLE_OAUTH_SECRETS_FILE'], ['email'], auth_code)

    email = credentials.id_token['email']

    # Lookup or store user in user persistence.
    user = current_app.user_mgmt.load(email) or \
        current_app.user_mgmt.create_by_id(email)

    # Use flask-login to persist login via session
    login_user(user, remember=True, duration=timedelta(hours=1))

    # Store refresh token in session to allow revoking token programatically.
    session['refresh_token'] = credentials.refresh_token
    return jsonify(user_auth_status())
