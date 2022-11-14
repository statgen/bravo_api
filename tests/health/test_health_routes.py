from bravo_api.blueprints.health import health
from flask import Flask

app = Flask('dummy')
app.register_blueprint(health.bp)


def test_heath_response_with_alive():
    with app.test_client() as client:
        resp = client.get('/health')
    content = resp.get_json()

    assert(resp.content_type == 'application/json')
    assert(content['alive'] is True)


def test_returns_unknown_version_when_undefined():
    with app.test_client() as client:
        resp = client.get('/version')
    content = resp.get_json()

    assert(resp.content_type == 'application/json')
    assert(content['version'] == 'unknown')


def test_returns_version_when_defined():
    app.version = '1.2.3'
    with app.test_client() as client:
        resp = client.get('/version')
    content = resp.get_json()

    assert(resp.content_type == 'application/json')
    assert(content['version'] == app.version)
