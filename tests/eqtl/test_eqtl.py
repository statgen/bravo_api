from bravo_api.blueprints.eqtl import eqtl
from flask import Flask

app = Flask('dummy')
app.register_blueprint(eqtl.bp)

# Test using fixture containing  "ENSG00000239920" and "ENSG00000244734"
# Gene names CTD-2643I7.5 and HBB respetively
SUSIE_EXPECTED = {"ENSG00000239920": 22, "ENSG00000244734": 0}
COND_EXPECTED = {"ENSG00000239920": 5, "ENSG00000244734": 2}


def test_susie_count(mocker, mongodb):
    # Mock PyMongo's database with pytest-mongo's fixtures
    pymongo_mock = mocker.Mock()
    pymongo_mock.db = mongodb
    app.mmongo = pymongo_mock

    # Mock the app's cache to return None (no caching)
    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=None)
    app.cache = cache_mock

    with app.test_client() as client:
        for id in SUSIE_EXPECTED:
            resp = client.get('/eqtl/susie_count', query_string={'ensembl': id})
            assert(resp.content_type == 'application/json')
            assert(resp.get_json() == SUSIE_EXPECTED[id])


def test_cond_count(mocker, mongodb):
    # Mock PyMongo's database with pytest-mongo's fixtures
    pymongo_mock = mocker.Mock()
    pymongo_mock.db = mongodb
    app.mmongo = pymongo_mock

    # Mock the app's cache to return None (no caching)
    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=None)
    app.cache = cache_mock

    with app.test_client() as client:
        for id in COND_EXPECTED:
            resp = client.get('/eqtl/cond_count', query_string={'ensembl': id})
            assert(resp.content_type == 'application/json')
            assert(resp.get_json() == COND_EXPECTED[id])
