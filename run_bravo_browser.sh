#!/bin/bash
#source venv/bin/activate
export FLASK_APP=bravo_browser

flask run --port 8089

#gunicorn -b 127.0.0.1:8089 -w 10 -k gevent "bravo_browser:create_app()"
