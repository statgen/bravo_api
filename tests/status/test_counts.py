from bravo_api.blueprints.status import status
from flask import Flask

app = Flask('dummy')
app.register_blueprint(status.bp)

# Total expected documents counts set at time of fixuture creating in tests/mongo_fixtures/
TOTAL_SNV_EXPECTED = 10
TOTAL_TRANSCRIPT_EXPECTED = 1
TOTAL_GENE_EXPECTED = 3


def test_count_collection(mongodb):
    snv_result = status.count_collection(mongodb.snv)
    trx_result = status.count_collection(mongodb.transcripts)
    gene_result = status.count_collection(mongodb.genes)

    assert(snv_result == TOTAL_SNV_EXPECTED)
    assert(trx_result == TOTAL_TRANSCRIPT_EXPECTED)
    assert(gene_result == TOTAL_GENE_EXPECTED)


def test_counts_aggregation(mocker, mongodb):
    # Mock PyMongo's database with pytest-mongo's fixtures
    pymongo_mock = mocker.Mock()
    pymongo_mock.db = mongodb
    app.mmongo = pymongo_mock

    # Mock the app's cache to return None (no caching)
    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=None)
    app.cache = cache_mock

    expected = {'snvs': TOTAL_SNV_EXPECTED,
                'transcripts': TOTAL_TRANSCRIPT_EXPECTED,
                'genes': TOTAL_GENE_EXPECTED}

    with app.test_client() as client:
        resp = client.get('/counts')
    content = resp.get_json()

    assert(resp.content_type == 'application/json')
    assert(content == expected)


def test_counts_cached_value_skips_query(mocker):
    # Mock the app's cache to return cached value
    cached = {'snvs': 300, 'transcripts': 200, 'genes': 100}

    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=cached)
    app.cache = cache_mock

    spy = mocker.spy(status, 'count_collection')

    with app.test_client() as client:
        client.get('/counts')

    spy.assert_not_called()


def test_no_counts_cached_does_query(mocker):
    # Mock the app's cache to return cached value
    cache_mock = mocker.Mock()
    cache_mock.get = mocker.Mock(return_value=None)
    app.cache = cache_mock

    spy = mocker.spy(status, 'count_collection')

    with app.test_client() as client:
        client.get('/counts')

    spy.assert_called()
