from bravo_browser import create_app
import pytest


@pytest.fixture
def app():
    app = create_app({
       'MONGO_URI': 'mongodb://localhost:27017/example',
       'COVERAGE_DIR': '',
       'SEQUENCES_DIR': '',
       'SEQUENCES_CACHE_DIR': '',
       'REFERENCE_SEQUENCE': '',
       'BRAVO_API_PAGE_LIMIT': 100000,
       'GZIP_COMPRESSION': True,
       'URL_PREFIX': ''
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def config(app):
    return app.config
