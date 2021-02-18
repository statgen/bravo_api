import pytest
from unittest.mock import patch
from bravo_browser import create_app
import bravo_browser.models.database
from mongomock import MongoClient


class PyMongoMock(MongoClient):
    def init_app(self, app):
        return super().__init__()

@pytest.fixture
def app():
    # TO MOCK: from bravo_browser.models.database import get_db()
    # Swap out with PyMongoMock(MongoClient)
    with patch.object(bravo_browser.models.database, "mongo", PyMongoMock()):
        app = create_app({
            'PROXY': False,
            'SECRET_KEY': b'deadbeef',
            'URL_PREFIX': '',
            'MONGO_URI': 'mongodb://localhost:27017/bravo-demo',
            'BRAVO_API_URI': 'http://localhost:9099',
            'GZIP_COMPRESSION': True,
            'GOOGLE_OAUTH_CLIENT_SECRET': '',
            'SUBTITLE': '',
            'DATASET_SHORT_NAME': '',
            'ARCHIVES': [],
            'DOWNLOADS': False,
            'DOWNLOAD_LABEL': 'Downloads',
            'DOWNLOAD_CHROMOSOMES_VCF': {},
            'DOWNLOAD_CHROMOSOMES_COVERAGE': {},
            'GOOGLE_ANALYTICS_TRACKING_ID': ''
        })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def config(app):
    return app.config
