from flask import Flask
from os import getenv
from bravo_api.models.sequences import init_sequences
from bravo_api.models.database import mongo
from bravo_api.models.coverage import init_coverage
from bravo_api.blueprints.api import api
from bravo_api.blueprints.legacy_ui import autocomplete, pretty_routes, gene_routes
from bravo_api.blueprints.health import health


def create_app(test_config=None):
    instance_path = getenv('BRAVO_API_INSTANCE_DIR', None)
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)

    if test_config is None:
        app.config.from_object('config.api_default')
        app.config.from_pyfile('api_config.py', silent=True)
        app.config.from_envvar('BRAVO_API_CONFIG_FILE', silent=True)
    else:
        app.config.from_mapping(test_config)

    mongo.init_app(app)

    init_coverage(app.config['COVERAGE_DIR'])

    init_sequences(app.config['SEQUENCES_DIR'],
                   app.config['REFERENCE_SEQUENCE'],
                   app.config['SEQUENCES_CACHE_DIR'])

    app.register_blueprint(api.bp)
    app.register_blueprint(health.bp)
    app.register_blueprint(autocomplete.bp, url_prefix='/ui')
    app.register_blueprint(pretty_routes.bp, url_prefix='/ui')
    app.register_blueprint(gene_routes.bp, url_prefix='/ui')

    if app.config['GZIP_COMPRESSION']:
        app.config['COMPRESS_MIMETYPES'] = ['application/json']
        app.config['COMPRESS_LEVEL'] = 3
        app.config['COMPRESS_MIN_SIZE'] = 500
        api.compress.init_app(app)

    return app
