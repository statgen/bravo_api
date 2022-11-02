from bravo_api.blueprints.bailiff import auth_routes, DummyUserMgmt
from flask import Flask, Blueprint
from flask_login import FlaskLoginClient

app = Flask('dummy')
app.config['SECRET_KEY'] = 'testonlysecret'
app.test_client_class = FlaskLoginClient

req_auth_bp = Blueprint('req_auth', __name__)
req_agree_bp = Blueprint('req_agree', __name__)

req_auth_bp.before_request(auth_routes.authentication_required)
req_agree_bp.before_request(auth_routes.agreement_required)


@req_auth_bp.route('/check')
def auth_check():
    return "Auth Success"


@req_agree_bp.route('/check')
def agree_check():
    return "Agree Success"


app.register_blueprint(auth_routes.bp)
app.register_blueprint(req_auth_bp, url_prefix="/auth")
app.register_blueprint(req_agree_bp, url_prefix="/agree")

auth_routes.init_user_management(app, DummyUserMgmt)


def test_auth_unauthorized():
    with app.test_client() as client:
        resp = client.get('/auth/check')
    assert(resp.status_code == 401)


def test_agree_unauthorized():
    with app.test_client() as client:
        resp = client.get('/agree/check')
    assert(resp.status_code == 401)


def test_auth_authorize():
    authed_user = app.user_mgmt.create_by_id('foo@example.com')
    with app.test_client(user=authed_user) as client:
        resp = client.get('/auth/check')
    assert(resp.status_code == 200)


def test_agree_authorize_no_agreement():
    authed_user = app.user_mgmt.create_by_id('bar@example.com')
    with app.test_client(user=authed_user) as client:
        resp = client.get('/agree/check')
    assert(resp.status_code == 403)


def test_agree_authorize_and_agreement():
    agreed_user = app.user_mgmt.create_by_id('baz@example.com')
    agreed_user = app.user_mgmt.update_agreed_to_terms(agreed_user)
    print("Debug----")
    print(agreed_user.agreed_to_terms)
    with app.test_client(user=agreed_user) as client:
        resp = client.get('/agree/check')
    assert(resp.status_code == 200)


def test_terms_emits_array():
    with app.test_client() as client:
        resp = client.get('/terms')
    assert(resp.status_code == 200)
    assert(resp.mimetype == 'application/json')


def test_agree_to_terms_unauthorized():
    with app.test_client() as client:
        resp = client.post('/agree_to_terms')
    assert(resp.status_code == 401)


def test_agree_to_terms_authorized():
    authed_user = app.user_mgmt.create_by_id('duq@example.com')
    assert(not authed_user.agreed_to_terms)

    with app.test_client(user=authed_user) as client:
        resp = client.post('/agree_to_terms')

    assert(authed_user.agreed_to_terms)
    assert(resp.status_code == 200)
