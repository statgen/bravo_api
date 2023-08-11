import json
from bravo_api.blueprints.bailiff import auth_routes, DummyUserMgmt, User
from flask import Flask
from flask_login import FlaskLoginClient


app = Flask('dummy')
app.config['SECRET_KEY'] = 'testonlysecret'
app.test_client_class = FlaskLoginClient

app.config['LOGIN_DISABLED'] = False
app.user_mgmt = DummyUserMgmt()
auth_routes.initialize(app)
app.register_blueprint(auth_routes.bp)

dummy_user = User('test@example.com', True)
app.user_mgmt.save(dummy_user)


def test_auth_status_structure():
    expected = {'active': True, 'agreed_to_terms': True, 'authenticated': True,
                'login_disabled': False, 'user': 'test@example.com'}
    with app.test_client(user=dummy_user) as client:
        resp = client.get('/auth_status')
        result = json.loads(resp.data)
        print(resp.data)
    assert(result == expected)
