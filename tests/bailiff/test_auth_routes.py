import pytest
import json
from bravo_api.blueprints.bailiff import auth_routes, DummyUserMgmt, User
from flask import Flask
from flask_login import FlaskLoginClient


@pytest.fixture(name="app_nc")
def app_not_configured():
    app = Flask('notconfigured')
    yield app

@pytest.fixture(name="app")
def app_configured():
    app = Flask('dummy')

    app.config['SECRET_KEY'] = 'testonlysecret'
    app.test_client_class = FlaskLoginClient
    app.config['LOGIN_DISABLED'] = False
    app.user_mgmt = DummyUserMgmt()

    auth_routes.initialize(app)
    app.register_blueprint(auth_routes.bp)

    yield app


def test_default_user_mgmt(app_nc, caplog):
    expected_message = "App does not have user_mgmt configured"

    auth_routes.initialize(app_nc)

    assert(isinstance(app_nc.user_mgmt, DummyUserMgmt))
    assert(expected_message in caplog.text)


def test_auth_status_structure(app):
    dummy_user = User(email='test@example.com', agreed_to_terms=True)
    app.user_mgmt.save(dummy_user)

    expected = {'active': True, 'agreed_to_terms': True, 'authenticated': True,
                'login_disabled': False, 'user': 'test@example.com'}
    with app.test_client(user=dummy_user) as client:
        resp = client.get('/auth_status')
        result = json.loads(resp.data)
        print(resp.data)
    assert(result == expected)
