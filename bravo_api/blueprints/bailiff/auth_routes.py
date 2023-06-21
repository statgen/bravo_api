"""@package Bailiff Routes
Authorization endpoints and login manager config.
"""
from flask import (Blueprint, current_app, jsonify, make_response, request,
                   redirect, url_for, session)
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from webargs.flaskparser import FlaskParser
from webargs import fields
from marshmallow import EXCLUDE
from datetime import timedelta
from .mongo_user_mgmt import MongoUserMgmt
from .anon_user import BravoAnonUser
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

    login_manager.anonymous_user = BravoAnonUser
    login_manager.user_loader(app.user_mgmt.load)
    login_manager.init_app(app)


def user_auth_status():
    return({'user': current_user.get_id(),
            'authenticated': current_user.is_authenticated,
            'agreed_to_terms': current_user.agreed_to_terms,
            'active': current_user.is_active,
            'login_disabled': current_app.config.get('LOGIN_DISABLED')})


def authentication_required():
    """
    Before request hook to be registered when all routes in blueprint should require auth.
    """
    if request.method == 'OPTIONS':
        return None
    elif current_app.config.get('LOGIN_DISABLED'):
        return None
    elif current_user.is_authenticated:
        return None
    else:
        resp = {'message': 'Authentication required.'}
        return(make_response(jsonify(resp), 401))


def agreement_required():
    """
    Before request hook to be registered when all routes in blueprint should require auth
      and agreement to the terms
    """
    if request.method == 'OPTIONS':
        return None
    elif current_app.config.get('LOGIN_DISABLED'):
        return None
    elif current_user.is_authenticated and current_user.agreed_to_terms:
        return None
    elif current_user.is_authenticated and not current_user.agreed_to_terms:
        resp = {'message': 'Agree to terms required.'}
        return(make_response(jsonify(resp), 403))
    else:
        resp = {'message': 'Authentication required.'}
        return(make_response(jsonify(resp), 401))


login_argmap = {'dest': fields.Str(required=False, missing=None)}


@bp.route('/login')
@parser.use_kwargs(login_argmap, location='query')
def login(dest):
    if(request.host.split(':')[0] == 'localhost'):
        scheme = 'http'
    else:
        scheme = 'https'

    redirect_uri = url_for('.acf', _external=True, _scheme=scheme)
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
    return make_response("Unauthorized: Must be logged in.", 401)


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return jsonify(user_auth_status())


@bp.route('/agree_to_terms', methods=['POST'])
@login_required
def agree_to_terms():
    current_app.user_mgmt.update_agreed_to_terms(current_user)
    return jsonify(user_auth_status())


@bp.route('/terms', methods=['GET'])
def terms():
    terms = ["You will not attempt to download any dataset in bulk from this website.",
             "You will not attempt to re-identify or contact research participants.",
             "You will protect data confidentiality.",
             ("You will report any inadvertent data release, security breach or other "
              "data management incident of which you become aware."),
             "You will abide by all applicable laws and regulations for handling genomic data.",
             ("You will not share data from this site with others.  Instead, please direct them "
              " to this site, dbGaP, or elsewhere to view this data.")]
    return jsonify(terms)
