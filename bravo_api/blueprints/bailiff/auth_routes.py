"""@package Bailiff Routes
Provide authorization endpoints.
Provide login_manager.
"""
from flask import Blueprint, current_app, jsonify, url_for, request, redirect, session, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from webargs.flaskparser import FlaskParser
from webargs import fields
from marshmallow import EXCLUDE
from datetime import timedelta
import requests
import json
from .dummy_user_mgmt import DummyUserMgmt

from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token


class Parser(FlaskParser):
    DEFAULT_UNKNOWN_BY_LOCATION = {"json": EXCLUDE}

login_manager = LoginManager()
bp = Blueprint('auth_routes', __name__)
parser = Parser()
oauth = OAuth()

def init_auth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'email'})


login_argmap = { 'dest': fields.Str(required=False, missing='/') }

@bp.route('/login')
@parser.use_kwargs(login_argmap, location='query')
def login(dest):
    redirect_uri = url_for('.acf', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


# Debugging & Testing Auth Code Flow
@bp.route('/acf', methods=['GET'])
def acf():
    token = oauth.google.authorize_access_token()
    # Automatic parsing token not behaving as expected.
    #   https://github.com/authlib/demo-oauth-client/issues/20
    userinfo = oauth.google.parse_id_token(token, None)

    email = userinfo['email']

    # Lookup or store user in user persistence.
    user = current_app.user_mgmt.load(email) or \
        current_app.user_mgmt.create_by_id(email)

    # Use flask-login to persist login via session
    login_user(user, remember=True, duration=timedelta(hours=1))

    return redirect('http://localhost:8080/login.html')


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
