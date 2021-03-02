from bravo_api import create_app
import pytest


@pytest.fixture
def app():
    app = create_app({
       'MONGO_URI': 'mongodb://localhost:27017/example',
       'COVERAGE_DIR': '/var/bravo/data/coverage',
       'SEQUENCES_DIR': '/var/bravo/data/crams',
       'SEQUENCES_CACHE_DIR': '/var/bravo/data/cache',
       'REFERENCE_SEQUENCE': '/var/bravo/data/reference/hs38DH.fa',
       'BRAVO_API_PAGE_LIMIT': 100000,
       'GZIP_COMPRESSION': True
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def config(app):
    return app.config
