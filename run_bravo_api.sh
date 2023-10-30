#!/bin/sh

# Activate venv if present.
[ -d 'venv' ] && source 'venv/bin/activate'

# This should be False in production
export FLASK_DEBUG=True

export FLASK_APP=bravo_api
export BRAVO_API_CONFIG_FILE='config.py'
export BRAVO_API_INSTANCE_DIR='./instance'

# Development server
flask run --port 9099

# Production server should use something like gunicorn
# gunicorn -b 127.0.0.1:9099 -w 10 -k gevent "bravo_api:create_app()"
