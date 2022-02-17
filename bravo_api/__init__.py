from flask import Flask
from os import getenv
from bravo_api.models.sequences import init_sequences
from bravo_api.models.database import mongo
from bravo_api.models.coverage import init_coverage
from bravo_api.blueprints.legacy_ui import autocomplete, variant_routes, gene_routes, region_routes
from bravo_api.blueprints.health import health
from bravo_api.blueprints.bailiff import auth_routes
from flask_cors import CORS
import secrets


def create_app(test_config=None):
    instance_path = getenv('BRAVO_API_INSTANCE_DIR', None)
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)

    if test_config is None:
        app.config.from_object('bravo_api.default_config')
        app.config.from_pyfile('api_config.py', silent=True)
        app.config.from_envvar('BRAVO_API_CONFIG_FILE', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Initialize persistence layer depenencies
    mongo.init_app(app)

    init_coverage(app.config['COVERAGE_DIR'])

    init_sequences(app.config['SEQUENCES_DIR'],
                   app.config['REFERENCE_SEQUENCE'],
                   app.config['SEQUENCES_CACHE_DIR'])

    # Initialize CORS and Sessions
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    app.secret_key = app.config['SESSION_SECRET'] or secrets.token_bytes()

    # Initialize routes
    app.register_blueprint(health.bp)
    app.register_blueprint(autocomplete.bp, url_prefix='/ui')
    app.register_blueprint(variant_routes.bp, url_prefix='/ui')
    app.register_blueprint(region_routes.bp, url_prefix='/ui')
    app.register_blueprint(gene_routes.bp, url_prefix='/ui')
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')

    # Initialize login manager
    auth_routes.init_user_management(app)

    return app
