from flask import Flask
from os import getenv


def create_app(test_config=None):
    instance_path = getenv('BRAVO_API_INSTANCE_DIR', 'instance')
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)

    if test_config is None:
        app.config.from_object('config.api_default')
        app.config.from_pyfile('api_config.py', silent=True)
        app.config.from_envvar('BRAVO_API_CONFIG_FILE', silent=True)
    else:
        app.config.from_mapping(test_config)

    from bravo_api.models.database import mongo, create_users, load_sv, load_snv, load_genes, load_qc_metrics
    mongo.init_app(app)
    app.cli.add_command(create_users)
    app.cli.add_command(load_sv)
    app.cli.add_command(load_snv)
    app.cli.add_command(load_genes)
    app.cli.add_command(load_qc_metrics)

    from bravo_api.models.coverage import init_coverage
    init_coverage(app.config['COVERAGE_DIR'])

    from bravo_api.models.sequences import init_sequences
    init_sequences(app.config['SEQUENCES_DIR'], app.config['REFERENCE_SEQUENCE'], app.config['SEQUENCES_CACHE_DIR'])

    from bravo_api import api
    app.register_blueprint(api.bp)

    if app.config['GZIP_COMPRESSION']:
        app.config['COMPRESS_MIMETYPES'] = ['application/json']
        app.config['COMPRESS_LEVEL'] = 3
        app.config['COMPRESS_MIN_SIZE'] = 500
        api.compress.init_app(app)

    return app
