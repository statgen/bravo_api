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
    app.user_mgmt = user_management

    login_manager.init_app(app)
    login_manager.user_loader(app.user_mgmt.load)


@bp.route('/auth_status')
def auth_status():
    if current_user.is_anonymous:
        data = {'user': current_user.get_id(),
                'authenticated': current_user.is_authenticated,
                'active': current_user.is_active,
                'login_disabled': current_app.config.get('LOGIN_DISABLED')}
    else:
        data = {'user': current_user.get_id(),
                'authenticated': current_user.is_authenticated,
                'active': current_user.is_active,
                'login_disabled': current_app.config.get('LOGIN_DISABLED')}
    return jsonify(data)


@bp.route('/accessdenied')
@login_manager.unauthorized_handler
def access_denied():
    return "Access Denied"


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return auth_status()


# Supporting: Web server application flow
def build_authorization_url():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        current_app.config['GOOGLE_OAUTH_SECRETS_FILE'],
        scopes=['https://www.googleapis.com/auth/userinfo.email'])
    flow.redirect_uri = url_for('.auth_callback', _external=True)
    return flow.authorization_url(access_type='offline', prompt='consent',
                                  include_granted_scopes='true')


# End point for starting Web server application flow
@bp.route('/authorize')
def authorize():
    if current_user.is_anonymous:
        auth_url, state = build_authorization_url()
        # Store state in session as it's used to verify the returned request.
        session['state'] = state
        return redirect(auth_url)
    else:
        return auth_status()


# End point for completing Web server application flow
@bp.route('/auth_callback')
def auth_callback():
    # Retrieve state from session to verify the incoming callback request
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        current_app.config['GOOGLE_OAUTH_SECRETS_FILE'],
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email'],
        state=state)
    # Set same redirect uri as the initial auth request.
    flow.redirect_uri = url_for('.auth_callback', _external=True)

    # Turn around and request token from endpoint
    flow.fetch_token(authorization_response=request.url)
    # Build credentials class
    credentials = flow.credentials

    # Lookup user info endpoint from google accounts
    endpoint_resp = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    endpoint_resp.raise_for_status()
    openid_endpoints = json.loads(endpoint_resp.text)
    userinfo_endpoint = openid_endpoints['userinfo_endpoint']

    # Use access token to lookup user info from google.
    user_info_resp = requests.get(userinfo_endpoint,
                                  headers={'Authorization': f'Bearer {credentials.token}'})
    user_info_resp.raise_for_status()
    userinfo = json.loads(user_info_resp.text)

    # Lookup or store user in user persistence.
    user = current_app.user_mgmt.load(userinfo['email']) or \
        current_app.user_mgmt.save(userinfo['email'])

    # Use flask-login to persist login via session
    login_user(user, remember=True, duration=timedelta(hours=1))

    # Store refresh token in session to allow revoking token programatically.
    session['refresh_token'] = credentials.refresh_token

    return auth_status()


# End point for completing Server side flow.
@bp.route('/auth_code', methods=['POST'])
def auth_code():
    # Get code from post data
    auth_code = request.json.get('code')

    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        current_app.config['GOOGLE_OAUTH_SECRETS_FILE'], auth_code)

    email = credentials.id_token['email']

    # Lookup or store user in user persistence.
    user = current_app.user_mgmt.load(email) or \
        current_app.user_mgmt.create_by_id(email)

    # Use flask-login to persist login via session
    login_user(user, remember=True, duration=timedelta(hours=1))

    # Store refresh token in session to allow revoking token programatically.
    session['refresh_token'] = credentials.refresh_token
    return auth_status()
