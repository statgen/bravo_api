import pytest
from flask import Flask
from bravo_api.blueprints.legacy_ui import autocomplete


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(autocomplete.bp)
    return(app)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def config(app):
    return app.config
