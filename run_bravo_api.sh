#!/bin/bash
source venv/bin/activate
export FLASK_APP=bravo_api

#flask run --port XYZ

gunicorn -b 127.0.0.1:XYZ -w 10 -k gevent "bravo_api:create_app()"
