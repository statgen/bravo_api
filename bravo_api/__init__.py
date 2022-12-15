from flask import Flask
from os import getenv
import importlib.resources as pkg_resources
from bravo_api.models.sequences import init_sequences
from bravo_api.models.database import mongo
from bravo_api.models.coverage import init_coverage
from bravo_api.blueprints.legacy_ui import autocomplete, variant_routes, gene_routes, region_routes
from bravo_api.blueprints.health import health
from bravo_api.blueprints.bailiff import auth_routes
from bravo_api.core.fs_coverage_provider import FSCoverageProvider
from flask_cors import CORS
import secrets


def version():
    return(pkg_resources.read_text(__package__, 'VERSION').strip())


def create_app(test_config=None):
    instance_path = getenv('BRAVO_API_INSTANCE_DIR', None)
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)

    app.version = pkg_resources.read_text(__package__, 'VERSION').strip()

    if test_config is None:
        app.config.from_object('bravo_api.default_config')
        app.config.from_envvar('BRAVO_API_CONFIG_FILE', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Initialize persistence layer depenencies
    mongo.init_app(app)

    # Determine which CoverageProvider to use
    init_coverage(app.config['COVERAGE_DIR'])
    app.coverage_provider = FSCoverageProvider(app.config['COVERAGE_DIR'])

    # TODO: Issue #20. Log warnings from coverage provider.
    # coverage_warnings = app.coverage_provicer.evaluate_coverage()
    # app.logger.info(f'{len(coverage_warnings)} coverage warnings.')

    init_sequences(app.config['SEQUENCES_DIR'],
                   app.config['REFERENCE_SEQUENCE'],
                   app.config['SEQUENCES_CACHE_DIR'])

    # Initialize CORS and Sessions
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    app.secret_key = app.config['SESSION_SECRET'] or secrets.token_bytes()

    # Protect data endpoint blueprints
    variant_routes.bp.before_request(auth_routes.agreement_required)
    region_routes.bp.before_request(auth_routes.agreement_required)
    gene_routes.bp.before_request(auth_routes.agreement_required)

    # Initialize routes. Prefix "ui" are routes for the Vue user interface.
    app.register_blueprint(health.bp, url_prefix='/')
    app.register_blueprint(health.bp, name="healthui", url_prefix='/ui')
    app.register_blueprint(autocomplete.bp, url_prefix='/ui')
    app.register_blueprint(variant_routes.bp, url_prefix='/ui')
    app.register_blueprint(region_routes.bp, url_prefix='/ui')
    app.register_blueprint(gene_routes.bp, url_prefix='/ui')
    app.register_blueprint(auth_routes.bp, url_prefix='/ui')

    # Initialize login manager
    auth_routes.init_user_management(app)
    auth_routes.init_auth(app)

    return app
