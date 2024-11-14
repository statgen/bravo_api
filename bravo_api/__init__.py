from logging.config import dictConfig
from os import getenv, getcwd
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_caching import Cache
from cachelib import FileSystemCache
from bravo_api.models.database import mongo
from bravo_api.blueprints.legacy_ui import autocomplete, variant_routes, gene_routes, region_routes
from bravo_api.blueprints.status import status
from bravo_api.blueprints.eqtl import eqtl
from bravo_api.blueprints.bailiff import auth_routes
from bravo_api.blueprints.bailiff import DomainUser
from bravo_api.blueprints.bailiff import MongoUserMgmt
from bravo_api.core import CoverageProviderFactory
from bravo_api.core import CramSourceFactory
import secrets
import importlib.resources as pkg_resources

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'},
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'}
    },
    'loggers': {
        'bravo_api': {
            'propagate': False,
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    }
})


def version():
    return(pkg_resources.read_text(__package__, 'VERSION').strip())


def create_app(test_config=None):
    instance_path = getenv('BRAVO_API_INSTANCE_DIR', getcwd())
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)

    app.version = pkg_resources.read_text(__package__, 'VERSION').strip()

    if test_config is None:
        print(getcwd())
        app.config.from_object('bravo_api.default_config')
        app.config.from_envvar('BRAVO_API_CONFIG_FILE', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Initialize app cache
    app.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
    app.cache.init_app(app)

    # Initialize persistence layer depenencies
    mongo.init_app(app)
    app.mmongo = PyMongo(app)

    # Initialize coverage
    app.coverage_provider = CoverageProviderFactory.build(app.config['COVERAGE_DIR'])
    coverage_warnings = app.coverage_provider.evaluate_catalog()
    app.logger.info(f'{len(coverage_warnings)} coverage warnings.')
    for cov_warn in coverage_warnings:
        app.logger.debug(f'coverage warning: {cov_warn}')

    # Initialize crams
    cram_cache = FileSystemCache(cache_dir=app.config['SEQUENCES_CACHE_DIR'], threshold=1000)
    app.cram_source = CramSourceFactory.build(app.config['SEQUENCES_DIR'],
                                              app.config['REFERENCE_SEQUENCE'],
                                              cram_cache)

    # Initialize CORS and Sessions
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    app.secret_key = app.config['SESSION_SECRET'] or secrets.token_bytes()

    # Protect data endpoint blueprints
    variant_routes.bp.before_request(auth_routes.agreement_required)
    region_routes.bp.before_request(auth_routes.agreement_required)
    gene_routes.bp.before_request(auth_routes.agreement_required)
    eqtl.bp.before_request(auth_routes.agreement_required)

    # Setup routes to blueprints. Prefix "ui" are routes for the Vue user interface.
    app.register_blueprint(status.bp, url_prefix='/ui')
    app.register_blueprint(eqtl.bp, url_prefix='/ui')
    app.register_blueprint(autocomplete.bp, url_prefix='/ui')
    app.register_blueprint(variant_routes.bp, url_prefix='/ui')
    app.register_blueprint(region_routes.bp, url_prefix='/ui')
    app.register_blueprint(gene_routes.bp, url_prefix='/ui')
    app.register_blueprint(auth_routes.bp, url_prefix='/ui')

    # Initialize User Management and Authorization Routes
    if 'USER_DOMAIN_PERMITTED' in app.config and not app.config['USER_DOMAIN_PERMITTED'] == "":
        DomainUser.set_permitted_domain(app.config['USER_DOMAIN_PERMITTED'])
        app.user_mgmt = MongoUserMgmt(app.mmongo, DomainUser)
    else:
        app.user_mgmt = MongoUserMgmt(app.mmongo)
    auth_routes.initialize(app)

    return app
