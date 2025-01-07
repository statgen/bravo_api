from bravo_api import create_app
import pytest


@pytest.fixture
def app():
    app = create_app({
        'MONGO_URI': 'mongodb://localhost:27017/bravo-demo',
        'COVERAGE_DIR': '/var/local/bravo/data/runtime/coverage',
        'SEQUENCES_DIR': '/var/local/bravo/data/runtime/crams',
        'SEQUENCES_CACHE_DIR': '/var/local/bravo/data/runtime/cache',
        'REFERENCE_SEQUENCE': '/var/local/bravo/data/runtime/reference/hs38DH.fa',
        'BRAVO_API_PAGE_LIMIT': 100000,
        'LOGIN_DISABLED': True
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def config(app):
    return app.config
