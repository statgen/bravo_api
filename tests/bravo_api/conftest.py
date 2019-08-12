import os
from bravo_api import create_app
import pytest


@pytest.fixture
def app():
   app = create_app({
      'MONGO_URI': 'mongodb://localhost:27017/example',
      'COVERAGE_DIR': '/data/bravo/coverage/TOPMed_freeze5_hg38/',
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
