from flask import Flask


def create_app(test_config = None):
   app = Flask(__name__, instance_relative_config = True)
   
   if test_config is None:
      app.config.from_object('config.web_default')
      app.config.from_pyfile('web_config.py', silent = True)
      app.config.from_envvar('BRAVO_BROWSER_CONFIG_FILE', silent = True)
   else:
      app.config.from_mapping(test_config)

   from bravo_browser.models.database import mongo, create_users, load_whitelist
   mongo.init_app(app)
   app.cli.add_command(create_users)
   app.cli.add_command(load_whitelist)

   from bravo_browser import browser
   app.register_blueprint(browser.bp, url_prefix = app.config['URL_PREFIX'])
   if app.config['GZIP_COMPRESSION']:
      app.config['COMPRESS_MIMETYPES'] = ['application/json']
      app.config['COMPRESS_LEVEL'] = 3
      app.config['COMPRESS_MIN_SIZE'] = 500
      browser.compress.init_app(app)
   browser.login_manager.init_app(app)

   return app
