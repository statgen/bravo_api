from flask import current_app, Blueprint, request, jsonify, make_response, abort, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
from flask_compress import Compress
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
import google_auth_oauthlib.flow
import functools
import requests
from webargs.flaskparser import parser
from webargs import fields, ValidationError
from datetime import timedelta
import re
import json
import urllib.parse
from bravo_browser.models import users

bp = Blueprint('browser', __name__, template_folder='templates', static_folder='static')
CORS(bp)

compress = Compress()
login_manager = LoginManager()


class User(UserMixin):
   pass


@login_manager.user_loader
def user_loader(email):
   document = users.load(email)
   if document is None:
      return None
   user = User()
   user.id = document['user_id']
   user.picture = document['picture']
   user.agreed_to_terms = document['agreed_to_terms']
   return user


def get_authorization_url():
   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
      scopes = ['openid', 'https://www.googleapis.com/auth/userinfo.email'])
   flow.redirect_uri = url_for('.oauth2callback', _external = True, _scheme = 'https')
   return flow.authorization_url(access_type = 'offline', include_granted_scopes = 'true')
 

def require_authorization(func):
   @functools.wraps(func)
   def authorization_wrapper(*args, **kwargs):
      if current_app.config['GOOGLE_OAUTH_CLIENT_SECRET']:
         if current_user.is_anonymous:
            authorization_url, state = get_authorization_url()
            session['state'] = state
            session['original_request_path'] = request.path
            return redirect(authorization_url)
         if not hasattr(current_user, 'agreed_to_terms') or not current_user.agreed_to_terms:
            session['original_request_path'] = request.path
            return redirect(url_for('.terms'))
      return func(*args, **kwargs)
   return authorization_wrapper


@bp.route('/oauth2callback', methods = ['GET', 'POST'])
def oauth2callback():
   state = session['state']
   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
      scopes = ['openid', 'https://www.googleapis.com/auth/userinfo.email'],
      state = state)
   flow.redirect_uri = url_for('.oauth2callback', _external = True, _scheme = 'https')
   if current_app.config['PROXY'] and not request.url.startswith('https'): # current version of Google OAuth python library doesn't handle situation when behind HTTPS proxy server
      protocol = request.headers.get('X-Forwarded-Proto', '')
      if protocol == 'https':
          authorization_response = re.sub(r'^http:', 'https:', request.url)
   else:
      authorization_response = request.url
   flow.fetch_token(authorization_response = authorization_response)
   credentials = flow.credentials

   response = requests.get('https://accounts.google.com/.well-known/openid-configuration') 
   response.raise_for_status()
   openid_endpoints = json.loads(response.text)
   userinfo_endpoint = openid_endpoints['userinfo_endpoint']
 
   response = requests.get(userinfo_endpoint, headers = { 'Authorization': f'Bearer {credentials.token}' })
   response.raise_for_status()
   userinfo = json.loads(response.text)

   if not users.in_whitelist(userinfo['email']):
      abort(403)

   document = users.load(userinfo['email'])
   if document is None:
      document = users.save(userinfo['email'], userinfo['picture'])

   user = User()
   user.id = userinfo['email']
   user.picture = userinfo['picture']

   if user.picture != document['picture']:
      users.update_picture(user.id, user.picture)
 
   login_user(user, remember = True, duration = timedelta(days = 1))
   return redirect(session.pop('original_request_path', url_for('.home'))) 


@bp.route('/about', methods = ['GET'])
def about():
   return render_template('about.html', show_brand = True, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '')


@bp.route('/terms', methods = ['GET'])
def terms():
   return render_template('terms.html', show_brand = True, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '')
   

@bp.route('/downloads', methods = ['GET'])
@require_authorization
def downloads():
   return render_template('downloads.html', show_brand = True, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '')


@bp.route('/downloads/vcf/<string:chromosome>', methods = ['GET'])
@require_authorization
def download_vcf(chromosome):
   if not chromosome in current_app.config['DOWNLOAD_CHROMOSOMES_VCF']:
      abort(404)
   return make_response(send_file(current_app.config['DOWNLOAD_CHROMOSOMES_VCF'][chromosome][1], as_attachment = True, mimetype='application/gzip'))


@bp.route('/downloads/coverage/<string:chromosome>', methods = ['GET'])
@require_authorization
def download_coverage(chromosome):
   if not chromosome in current_app.config['DOWNLOAD_CHROMOSOMES_COVERAGE']:
      abort(404)
   return make_response(send_file(current_app.config['DOWNLOAD_CHROMOSOMES_COVERAGE'][chromosome][1], as_attachment = True, mimetype='application/gzip'))


@bp.route('/agree_to_terms', methods = ['GET'])
def agree_to_terms():
   if current_app.config['GOOGLE_OAUTH_CLIENT_SECRET']:
     if not current_user.is_anonymous:
        current_user.agreed_to_terms = True
        users.update_agreed_to_terms(current_user.id, current_user.agreed_to_terms)
        return redirect(session.pop('original_request_path', url_for('.home')))
   abort(404)


@bp.route('/signin', methods = ['GET'])
def signin():
   if current_app.config['GOOGLE_OAUTH_CLIENT_SECRET']:
      authorization_url, state = get_authorization_url()
      session['state'] = state
      return redirect(authorization_url)
   abort(404)

   
@bp.route('/logout', methods = ['GET'])
def logout():
   if current_app.config['GOOGLE_OAUTH_CLIENT_SECRET']:
      logout_user()
      return redirect(url_for('.home'))
   abort(404)


@bp.route('/', methods = ['GET'])
def home():
   return render_template('home.html', show_brand = False, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '')


@bp.route('/autocomplete', methods = ['GET'])
def autocomplete():
   query = request.args.get('query', '')
   suggestions = []
   if query:
      api_response = requests.get(f"{current_app.config['BRAVO_API_URI']}/genes?name={query}")
      if api_response.status_code == 200:
         payload = api_response.json()
         if not payload['error']:
            for gene in payload['data']:
               suggestions.append({
                  'value': gene['gene_name'],
                  'data': {
                     'chrom': gene['chrom'],
                     'start': gene['start'],
                     'stop': gene['stop'],
                     'type': gene['gene_type']
                  } 
               })
   return make_response(jsonify({ "suggestions": suggestions }), 200)


# 1:1-1000
_regex_pattern_chr = r'^(?:CHR)?(\d+|X|Y|M|MT)'
_regex_pattern_chr_pos = _regex_pattern_chr + r'\s*[-:/]\s*([\d,]+)'
_regex_pattern_chr_start_end = _regex_pattern_chr_pos + r'\s*[-:/]\s*([\d,]+)'
_regex_pattern_chr_pos_ref_alt = _regex_pattern_chr_pos + r'\s*[-:/]\s*([ATCG]+)\s*[-:/]\s*([ATCG]+)'

_regex_chr = re.compile(_regex_pattern_chr+'$')
_regex_chr_pos = re.compile(_regex_pattern_chr_pos+'$')
_regex_chr_start_end = re.compile(_regex_pattern_chr_start_end+'$')
_regex_chr_pos_ref_alt = re.compile(_regex_pattern_chr_pos_ref_alt+'$')


@bp.route('/search', methods = ['GET'])
def search():
   arguments = {
      'value': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
      'chrom': fields.Str(required = False, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
      'start': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
      'stop': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'})
   }
   args = parser.parse(arguments)
   if 'value' in args and 'chrom' in args and 'start' in args and 'stop' in args: # suggested gene name
      args = {
         'variants_type': 'snv',
         'gene_name': args['value']
      }
      return redirect(url_for('.gene_page', **args))
   elif 'value' in args: # typed value
      match = _regex_chr_start_end.match(args['value'])
      if match is not None:
         args = {
            'variants_type': 'snv',
            'chrom': match.groups()[0],
            'start': match.groups()[1],
            'stop': match.groups()[2]}
         return redirect(url_for('.region_page', **args))
   return not_found(f'We coudn\'t find what you wanted.')


@bp.route('/not_found/<message>', methods = ['GET'])
@require_authorization
def not_found(message):
   return render_template('not_found.html', show_brand = True, message = message), 404


@bp.route('/region/<string:variants_type>/<string:chrom>-<int:start>-<int:stop>')
@require_authorization
def region_page(variants_type, chrom, start, stop):
   if variants_type not in ['snv', 'sv']:
      return not_found(f'We couldn\'t find what you wanted')
   return render_template('region.html', show_brand = True, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '', variants_type = variants_type, chrom = str(chrom), start = start, stop = stop)


@bp.route('/gene/<string:variants_type>/<string:gene_name>')
@require_authorization
def gene_page(variants_type, gene_name):
   if variants_type not in ['snv', 'sv']:
      return not_found(f'We couldn\'t find what you wanted')
   return render_template('gene.html', show_brand = True, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '', variants_type = variants_type, gene_name = gene_name)


@bp.route('/variant/<string:variant_type>/<string:variant_id>')
@require_authorization
def variant_page(variant_type, variant_id):
   if variant_type not in ['snv', 'sv']:
      return not_found(f'We couldn\'t find what you wanted')
   return render_template('variant.html', show_brand = True, show_signin = current_app.config['GOOGLE_OAUTH_CLIENT_SECRET'] != '', variant_id = variant_id)


@bp.route('/variant/api/snv/<string:variant_id>')
def variant(variant_id):
   arguments = {
      'variant_id': fields.Str(location = 'view_args', required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'})
   }
   args = parser.parse(arguments)
   api_response = requests.get(f"{current_app.config['BRAVO_API_URI']}/snv?variant_id={variant_id}", headers = { 'Accept-Encoding': 'gzip' })
   if api_response.status_code == 200:
      return make_response(api_response.content, 200)
   return not_found(f'I couldn\'t find what you wanted')


@bp.route('/qc/api')
def qc():
   api_response = requests.get(f"{current_app.config['BRAVO_API_URI']}/qc", headers = { 'Accept-Encoding': 'gzip' })
   if api_response.status_code == 200:
      return make_response(api_response.content, 200)
   return not_found(f'I couldn\'t find what you wanted')


@bp.route('/genes/<string:chrom>-<int:start>-<int:stop>')
@require_authorization
def genes(chrom, start, stop):
   arguments = {
      'chrom': fields.Str(location = 'view_args', required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
      'start': fields.Int(location = 'view_args', required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
      'stop': fields.Int(location = 'view_args', required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'})
   }
   args = parser.parse(arguments)
   api_response = requests.get(f"{current_app.config['BRAVO_API_URI']}/genes?chrom={chrom}&start={start}&stop={stop}&full=1", headers = { 'Accept-Encoding': 'gzip' })
   if api_response.status_code == 200:
      return make_response(api_response.content, 200)
   return not_found(f'I couldn\'t find what you wanted')


@bp.route('/genes/api/<string:name>')
@require_authorization
def genes_by_name(name):
   arguments = {
      'name': fields.Str(location = 'view_args', required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
   }
   args = parser.parse(arguments)
   api_response = requests.get(f"{current_app.config['BRAVO_API_URI']}/genes?name={name}&full=1", headers = { 'Accept-Encoding': 'gzip' })
   if api_response.status_code == 200:
      return make_response(api_response.content, 200)
   return not_found(f'I couldn\'t find what you wanted')


@bp.route('/coverage/<string:chrom>-<int:start>-<int:stop>', methods = ['POST'])
@require_authorization
def coverage(chrom, start, stop):
   arguments = {
      'chrom': fields.Str(location = 'view_args', required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
      'start': fields.Int(location = 'view_args', required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
      'stop': fields.Int(location = 'view_args', required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
      'size': fields.Int(location = 'json', required = True, validate = lambda x: x > 0, error_messages = {'validation_failed': 'Value must be greater then 0'}),
      'next': fields.Str(location = 'json', required = True, allow_none = True, validate = lambda x: len(x) > 0, error_message = {'validator_failed': 'Value must be a non-empty string.'})
   }
   args = parser.parse(arguments)
   if args['next'] is not None:
      url = f"{current_app.config['BRAVO_API_URI']}{args['next']}"
   else:
      url = f"{current_app.config['BRAVO_API_URI']}/coverage?chrom={chrom}&start={start}&stop={stop}&limit={args['size']}"
   api_response = requests.get(url, headers = { 'Accept-Encoding': 'gzip' })
   if api_response.status_code == 200:
      payload = api_response.json()
      if not payload['error'] and payload['next'] is not None:
         url = urllib.parse.urlparse(payload['next'])
         url = url._replace(scheme = '', netloc = '')
         payload['next'] = urllib.parse.urlunparse(url)
      response = make_response(jsonify(payload), 200)
      response.mimetype = 'application/json'
      return response
   return not_found(f'I coudn\'t find what you wanted')  


#@bp.route('/variants/<string:feature_type>/<string:variants_type>', methods = ['POST', 'GET'])
#@require_authorization
#def variants_meta(feature_type, variants_type):
@bp.route('/variants/<string:variants_type>', methods = ['POST', 'GET'])
@require_authorization
def variants_meta(variants_type):
   #url = f"{current_app.config['BRAVO_API_URI']}/{feature_type}/{variants_type}/filters"
   url = f"{current_app.config['BRAVO_API_URI']}/{variants_type}/filters"
   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404


@bp.route('/variants/region/<string:variants_type>/<string:chrom>-<int:start>-<int:stop>/histogram', methods = ['POST', 'GET'])
@require_authorization
def region_variants_histogram(variants_type, chrom, start, stop):
   sort = []
   args = []
   size = None
   url = None

   filter_type = {
      '=': 'eq',
      '!=': 'ne',
      '<': 'lt',
      'gt': 'gt',
      '<=': 'lte',
      '>=': 'gte'
   } 

   if request.method == 'POST':
      params = request.get_json()
      if params:
         for f in params.get('filters', []):
            args.append(f'{f["field"]}={filter_type.get(f["type"], "eq")}:{f["value"]}')
         if 'windows' in params:
            args.append(f'windows={params["windows"]}')

   url = f"{current_app.config['BRAVO_API_URI']}/region/{variants_type}/histogram?chrom={chrom}&start={start}&stop={stop}"
   if args:
      url += f"&{'&'.join(args)}"

   print(url)

   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404


@bp.route('/variants/region/<string:variants_type>/<string:chrom>-<int:start>-<int:stop>/summary', methods = ['POST', 'GET'])
@require_authorization
def region_variants_summary(variants_type, chrom, start, stop):
   url = f"{current_app.config['BRAVO_API_URI']}/region/{variants_type}/summary?chrom={chrom}&start={start}&stop={stop}"
   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404


@bp.route('/variants/gene/<string:variants_type>/<string:gene_name>/summary', methods = ['POST', 'GET'])
@require_authorization
def gene_variants_summary(variants_type, gene_name):
   url = f"{current_app.config['BRAVO_API_URI']}/gene/{variants_type}/summary?name={gene_name}"
   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404



@bp.route('/variants/gene/<string:variants_type>/<string:gene_name>/histogram', methods = ['POST', 'GET'])
@require_authorization
def gene_variants_histogram(variants_type, gene_name):
   sort = []
   args = []
   size = None
   url = None

   filter_type = {
      '=': 'eq',
      '!=': 'ne',
      '<': 'lt',
      'gt': 'gt',
      '<=': 'lte',
      '>=': 'gte'
   } 

   if request.method == 'POST':
      params = request.get_json()
      if params:
         print('gene histogram params = ', params)
         for f in params.get('filters', []):
            args.append(f'{f["field"]}={filter_type.get(f["type"], "eq")}:{f["value"]}')
         if 'windows' in params:
            args.append(f'windows={params["windows"]}')
         if 'introns' in params:
            args.append(f'introns={params["introns"]}')

   url = f"{current_app.config['BRAVO_API_URI']}/gene/{variants_type}/histogram?name={gene_name}"
   if args:
      url += f"&{'&'.join(args)}"

   print(url)

   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404


@bp.route('/variants/region/<string:variants_type>/<string:chrom>-<int:start>-<int:stop>', methods = ['POST', 'GET'])
@require_authorization
def variants(variants_type, chrom, start, stop):
   sort = []
   args = []
   size = None
   url = None

   filter_type = {
      '=': 'eq',
      '!=': 'ne',
      '<': 'lt',
      'gt': 'gt',
      '<=': 'lte',
      '>=': 'gte'
   } 

   if request.method == 'POST':
      params = request.get_json()
      if params:
         if 'next' in params and params['next'] is not None:
            url = params['next']
         if 'size' in params:
            size = int(params['size'])
         for f in params.get('filters', []):
            args.append(f'{f["field"]}={filter_type.get(f["type"], "eq")}:{f["value"]}')
         for s in params.get('sorters', []):
            sort.append(f'{s["field"]}:{s["dir"]}')

   if url is not None:
      url = f"{current_app.config['BRAVO_API_URI']}{url}"
   else:
      url = f"{current_app.config['BRAVO_API_URI']}/region/{variants_type}?chrom={chrom}&start={start}&stop={stop}"
      if size:
         url += f'&limit={size}'
      if args:
         url += f"&{'&'.join(args)}"
      if sort:
         url += f"&sort={','.join(sort)}"

   print(url)

   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      if not payload['error'] and payload['next'] is not None:
         # remove host url because we don't want to expose what is our api endpoint
         url = urllib.parse.urlparse(payload['next'])
         url = url._replace(scheme = '', netloc = '')
         payload['next'] = urllib.parse.urlunparse(url)
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404


@bp.route('/variants/gene/<string:variants_type>/<string:gene_name>', methods = ['POST', 'GET'])
@require_authorization
def gene_variants(variants_type, gene_name):
   sort = []
   args = []
   size = None
   url = None

   filter_type = {
      '=': 'eq',
      '!=': 'ne',
      '<': 'lt',
      'gt': 'gt',
      '<=': 'lte',
      '>=': 'gte'
   } 

   if request.method == 'POST':
      params = request.get_json()
      if params:
         print('params from browser = ', params)
         if 'next' in params and params['next'] is not None:
            url = params['next']
         if 'size' in params:
            size = int(params['size'])
         if 'introns' in params:
            args.append(f'introns={params["introns"]}')
         for f in params.get('filters', []):
            args.append(f'{f["field"]}={filter_type.get(f["type"], "eq")}:{f["value"]}')
         for s in params.get('sorters', []):
            sort.append(f'{s["field"]}:{s["dir"]}')

   if url is not None:
      url = f"{current_app.config['BRAVO_API_URI']}{url}"
   else:
      url = f"{current_app.config['BRAVO_API_URI']}/gene/{variants_type}?name={gene_name}"
      if size:
         url += f'&limit={size}'
      if args:
         url += f"&{'&'.join(args)}"
      if sort:
         url += f"&sort={','.join(sort)}"

   print('url to API = ', url)

   api_response = requests.get(url)
   if api_response.status_code == 200:
      payload = api_response.json()
      if not payload['error'] and payload['next'] is not None:
         # remove host url because we don't want to expose what is our api endpoint
         url = urllib.parse.urlparse(payload['next'])
         url = url._replace(scheme = '', netloc = '')
         payload['next'] = urllib.parse.urlunparse(url)
      return make_response(jsonify(payload), 200)
   return render_template('not_found.html', show_brand = True, message = "Bad query!"), 404
