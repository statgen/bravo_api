"""@package Bailiff Routes
Provide authorization endpoints.
Provide login_manager.
"""
from flask import (Blueprint, current_app, jsonify, make_response, request,
                   redirect, url_for, session)
from flask_login import LoginManager, current_user, login_user, logout_user
from webargs.flaskparser import FlaskParser
from webargs import fields
from marshmallow import EXCLUDE
from datetime import timedelta
from .mongo_user_mgmt import MongoUserMgmt
from authlib.integrations.flask_client import OAuth


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


def init_user_management(app, user_management=None):
    if user_management is None:
        user_management = MongoUserMgmt
    app.user_mgmt = user_management()

    login_manager.user_loader(app.user_mgmt.load)
    login_manager.init_app(app)


def user_auth_status():
    return({'user': current_user.get_id(),
            'authenticated': current_user.is_authenticated,
            'active': current_user.is_active,
            'login_disabled': current_app.config.get('LOGIN_DISABLED')}
           )


def authentication_required():
    if request.method == 'OPTIONS':
        return None
    elif current_app.config.get('LOGIN_DISABLED'):
        return None
    elif current_user.is_authenticated:
        return None
    else:
        resp = {'message': 'Authentication required.'}
        return(make_response(jsonify(resp), 403))


login_argmap = {'dest': fields.Str(required=False, missing=None)}


@bp.route('/login')
@parser.use_kwargs(login_argmap, location='query')
def login(dest):
    if(request.host.split(':')[0] == 'localhost'):
        scheme = 'http'
    else:
        scheme = 'https'

    redirect_uri = url_for('.acf', _external=True, _scheme=scheme)
    print(request.host)
    print(request.host.split(':')[0])
    session['dest'] = dest
    return oauth.google.authorize_redirect(redirect_uri)


# Auth Code Flow endpoint
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

    # if session has a destination, redirect there
    destination = session.get('dest')
    if destination is not None:
        return redirect(destination)
    else:
        return make_response(jsonify(user_auth_status()))


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
