from bravo_api.blueprints.status import status
from flask import Flask

app = Flask('dummy')
app.register_blueprint(status.bp)

# Expected results of mongo querying functions when using
#   the mongodb fixtures in tests/mongo_fixtures/
ACTIVE_USERS_EXPECTED = [{'month': 11, 'active_users': 10, 'year': 2023},
                         {'month': 10, 'active_users': 1, 'year': 2023},
                         {'month': 9, 'active_users': 2, 'year': 2023},
                         {'month': 8, 'active_users': 3, 'year': 2023}]

MAX_DAILY_EXPECTED = [{'max_user_per_day': 6, 'month': 11, 'year': 2023},
                      {'max_user_per_day': 1, 'month': 10, 'year': 2023},
                      {'max_user_per_day': 1, 'month': 9, 'year': 2023},
                      {'max_user_per_day': 1, 'month': 8, 'year': 2023}]

NEW_USERS_EXPECTED = [{'month': 10, 'new_users': 1, 'run_total': 4, 'year': 2023},
                      {'month': 9, 'new_users': 2, 'run_total': 3, 'year': 2023},
                      {'month': 8, 'new_users': 1, 'run_total': 1, 'year': 2023}]

TOTAL_USERS_EXPECTED = 4


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


def test_active_user_query(mongodb):
    result = status.active_user_count(mongodb.auth_log)
    assert(result == ACTIVE_USERS_EXPECTED)


def test_new_user_query(mongodb):
    result = status.new_user_count(mongodb.users)

    assert(len(result) == 3)
    assert(result == NEW_USERS_EXPECTED)


def test_total_user_query(mongodb):
    result = status.total_user_count(mongodb.users)
    assert(result == TOTAL_USERS_EXPECTED)


def test_usage_statistic(mongodb):
    expected = {"active": ACTIVE_USERS_EXPECTED,
                "new": NEW_USERS_EXPECTED,
                "total": TOTAL_USERS_EXPECTED,
                "max_user_per_day": MAX_DAILY_EXPECTED}

    result = status.usage_stats(mongodb)
    assert(result == expected)


def test_usage_endpoint(mocker, mongodb):
    # Mock PyMongo's database with pytest-mongo's fixtures
    pymongo_mock = mocker.Mock()
    pymongo_mock.db = mongodb
    app.mmongo = pymongo_mock

    # Mock the app's cache to return None (no caching)
    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=None)
    app.cache = cache_mock

    expected = {"active": ACTIVE_USERS_EXPECTED,
                "new": NEW_USERS_EXPECTED,
                "total": TOTAL_USERS_EXPECTED,
                "max_user_per_day": MAX_DAILY_EXPECTED}

    with app.test_client() as client:
        resp = client.get('/usage')
    content = resp.get_json()
    assert(content == expected)


def test_max_users_per_day(mocker, mongodb):
    result = status.max_users_per_day(mongodb.auth_log)
    assert(result == MAX_DAILY_EXPECTED)
