from bravo_api.blueprints.status import status
from flask import Flask
from unittest.util import unorderable_list_difference

app = Flask('dummy')
app.register_blueprint(status.bp)


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


def test_active_user_query(mocker, mongodb):
    # Mock PyMongo's database with pytest-mongo's fixtures
    pymongo_mock = mocker.Mock()
    pymongo_mock.db = mongodb
    app.mmongo = pymongo_mock

    expected = [{'month': 10, 'n_users': 1, 'year': 2023},
                {'month': 9, 'n_users': 2, 'year': 2023},
                {'month': 8, 'n_users': 3, 'year': 2023}]

    # Mock the app's cache to return None (no caching)
    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=None)
    app.cache = cache_mock

    with app.test_client() as client:
        resp = client.get('/usage')
    content = resp.get_json()
    (missing, unexpected) = unorderable_list_difference(content, expected)

    assert(resp.content_type == 'application/json')
    assert(len(content) == len(expected))
    assert((missing, unexpected) == ([], []))
