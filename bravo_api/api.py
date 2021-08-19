from flask import current_app, Blueprint, request, jsonify, make_response, abort, send_file
from flask_cors import CORS
from flask_compress import Compress
from webargs.flaskparser import FlaskParser, use_args
from webargs import fields, ValidationError
from marshmallow import RAISE
from bravo_api.models import variants, coverage, sequences, qc_metrics
import string
import re

import urllib
import json

bp = Blueprint('api', __name__)
CORS(bp)

compress = Compress()


class UserError(Exception):
    status_code = 400

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class Parser(FlaskParser):
    # Override to raise validation error for unknown args
    DEFAULT_UNKNOWN_BY_LOCATION = {"query": RAISE}


parser = Parser()


allowed_sv_sort_keys = {'pos': int, 'stop': int, 'support': int, 'avglen': int, 'filter': str,
                        'qual': float, 'type': str, 'variant_id': str}
allowed_snv_sort_keys = {
   'pos': int,
   'filter': str,
   'qual': float,
   'variant_id': str,
   'allele_num': int,
   'allele_freq': float,
   'hom_count': int,
   'het_count': int,
   'cadd_phred': float,
   'rsids': list,
   'annotation.region.lof': list,
   'annotation.region.consequence': list,
   'annotation.gene.lof': list,
   'annotation.gene.consequence': list
}


@parser.error_handler
def handle_http_request_parsing_error(error, request, schema, error_status_code, error_headers):
    for field, message in error.messages.items():
        user_message = f"Error while parsing {field} query parameter: {message}"
    response = make_response(jsonify({ 'data': None, 'total': None, 'limit': None, 'next': None, 'error': user_message }), 422)
    abort(response)


@bp.errorhandler(UserError)
def handle_user_error(error):
    response = make_response(jsonify({ 'data': None, 'total': None, 'limit': None, 'next': None, 'error': error.message }), error.status_code)
    return response


def validate_paging_args(parsed_args):
    if 'start' in parsed_args and 'stop' in parsed_args:
        if parsed_args['start'] >= parsed_args['stop']:
            raise ValidationError({'start': ['Start position must be greater than stop position.']})
    if 'limit' in parsed_args:
        if parsed_args['limit'] > current_app.config['BRAVO_API_PAGE_LIMIT']:
            raise ValidationError({'limit': [f'Page limit must be less than or equal to {current_app.config["BRAVO_API_PAGE_LIMIT"]}']})
    return True


def validate_variant_http_request_args(parsed_args):
    validate_paging_args(parsed_args)
    if 'variant_id' in parsed_args:
        try:
            chrom, pos, ref, alt = parsed_args['variant_id'].split('-')
            pos = int(pos)
        except:
            if not parsed_args['variant_id'].startswith('rs'):
                raise ValidationError({'variant_id': ['Invalid variant ID format.']})
    elif 'chrom' in parsed_args:
        if 'pos' not in parsed_args:
            raise ValidationError({'pos': ['Position is mandatory when chromosome is specified.']})
    elif 'pos' in parsed_args:
        if 'chrom' not in parsed_args:
            raise ValidationError({'chrom': ['Chromosome is mandatory when position is specified.']})
    else:
        raise ValidationError({'variant_id': ['Variant ID is mandatory if no other arguments are specified.']})
    return True


def deserialize_query_filter(value, value_type):
    value = value.strip()
    if len(value) == 0: # empty
        raise ValidationError('empty value')
    if len(value) > 1 and ((value[0] == '"' and value[-1] == '"'  ) or ( value[0] == '\'' and value[-1] == '\'')): # quoted -- treat everything as one value
        if value_type != str: # if value was quoted, then it must be a string
            raise ValidationError("invalid value type")
        operator = '$eq'
        value = value[1:-1]
        return {operator: [value]}
    else:
        conditions = {}
        for condition in value.split(','):
            elements = condition.split(':')
            if len(elements) == 1:
                operator = '$eq'
                value = elements[0]
            elif len(elements) == 2:
                operator = '${}'.format(elements[0].lower())
                value = elements[1]
                if operator not in ['$eq', '$ne', '$gt', '$lt', '$gte', '$lte', '$like']:
                    raise ValidationError('unknown comparison operator')
                if operator == '$like':
                    operator = '$regex'
                    value = '^' + value
            else:
                raise ValidationError('too many values for comparison operator')
            try: # checking data type
                if value_type == str:
                    if len(value) > 1 and ((value[0] == '"' and value[-1] == '"'  ) or ( value[0] == '\'' and value[-1] == '\'')): # if str and quoted, then remove quotes
                        value = value[1:-1]
                else:
                    value = value_type(value)
            except:
                raise ValidationError('invalid value type')
            conditions.setdefault(operator, []).append(value)
        return conditions


def deserialize_query_sort(values, allowed_sort_keys):
    query_sort = []
    values = values.strip()
    if len(values) == 0:
        raise ValidationError('empty argument')
    for value in (x.strip().split(':') for x in values.split(',')):
        if len(value) == 0 or len(value) > 2:
            raise ValidationError('invalid syntax')
        key = value[0].strip().lower()
        if key not in allowed_sort_keys:
            raise ValidationError(f"sort in not supported for '{key}'")
        direction = value[1].strip().lower() if len(value) > 1 else ''
        if direction == '' or direction == 'asc' or direction == '1':
            direction = 'asc'
        elif direction == 'desc' or direction == '-1':
            direction = 'desc'
        else:
            raise ValidationError(f"unknown sort direction '{direction}'")
        query_sort.append((key, direction))
    return query_sort


def deserialize_query_last(value, allowed_sort_keys):
    fields = json.loads(value)
    if type(fields) != dict or len(fields) == 0:
        raise ValidationError('Invalid value.')
    if not '_id' in fields:
        raise ValidationError('Invalid value.')
    for field_name, field_value in fields.items():
        if field_name == '_id':
            if len(field_value) != 24 or any(c not in string.hexdigits for c in field_value):
                raise ValidationError('Invalid value.')
        #elif field_name not in allowed_sort_keys:
        #   raise ValidationError('Invalid value.')
        #elif field_value is not None and allowed_sort_keys[field_name] != type(field_value):
        #   raise ValidationError('Invalid valie.')
    return fields


cov_argmap = {
    'chrom': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required = True, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than or equal to 0.'}),
    'stop': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'limit': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'last': fields.Int(required = False, validate = lambda x: x >= 0, error_messages = {'vlidator_failed': 'Value must be greater than or equal to 0.'})
}


@bp.route('/coverage', methods=['GET'])
@parser.use_args(cov_argmap, location='query', validate=validate_paging_args)
def get_coverage(args):
    args['limit'] = args.get('limit', current_app.config['BRAVO_API_PAGE_LIMIT'])  # Bad hack
    result = coverage.get_coverage(args['chrom'], args['start'], args['stop'], args['limit'], args.get('last', 0))
    url = None
    if result['last'] is not None:
        url = request.base_url + '?' + '&'.join(f'{arg}={value}' for arg, value in request.args.items(True) if arg != 'last')
        url += f'&last={result["last"]}'
    response = make_response(jsonify({ 'data': result['data'], 'total': result['total'], 'limit': args['limit'], 'next': url, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


snv_argmap = {
    'variant_id': fields.Str(required = False, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'chrom': fields.Str(required = False, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'pos': fields.Int(required = False, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'full': fields.Bool(required = False, missing = False)
}


@bp.route('/snv', methods=['GET'])
@parser.use_args(snv_argmap, location='query', validate=validate_variant_http_request_args)
def get_variant(args):
    data = []
    if 'variant_id' in args:
        for variant in variants.get_snv(args['variant_id'], None, None, args['full']):
            data.append(variant)
    elif all(x in args for x in ['chrom', 'pos']):
        for variant in variants.get_snv(None, args['chrom'], args['pos'], args['full']):
            data.append(variant)
    else:
        raise UserError('Invalid query parameters')
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


region_sv_argmap = {
    'chrom': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required = True, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than or equal to 0.'}),
    'stop': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'type': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'sort': fields.Function(deserialize = lambda x: deserialize_query_sort(x, allowed_sv_sort_keys)),
    'limit': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'last': fields.Function(deserialize = lambda x: deserialize_query_last(x, allowed_sv_sort_keys))
}


@bp.route('/region/sv', methods=['GET'])
@parser.use_args(region_sv_argmap, location='query', validate=validate_paging_args)
def get_region(args):
    args['limit'] = args.get('limit', current_app.config['BRAVO_API_PAGE_LIMIT'])  # Bad hack
    filter = { key: args[key] for  key in ['type', 'filter'] if key in args }
    result = variants.get_region(args['chrom'], args['start'], args['stop'], filter, args.get('sort', []), args.get('last', {}), args['limit'])
    url = None
    if result['last'] is not None:
        url = request.base_url + '?' + '&'.join(f'{arg}={value}' for arg, value in request.args.items(True) if arg != 'last' and arg != 'sort')
        url += '&sort=' + ','.join(f'{key}:{direction}' for key, direction in result['sort'])
        url += f'&last={result["last"]}'
    response = make_response(jsonify({ 'data': result['data'], 'total': result['total'], 'limit': result['limit'], 'next': url, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


region_snv_argmap = {
    'chrom': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required = True, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than or equal to 0.'}),
    'stop': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'allele_freq': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'annotation.region.lof': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'annotation.region.consequence': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'cadd_phred': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'rsids': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'sort': fields.Function(deserialize = lambda x: deserialize_query_sort(x, allowed_snv_sort_keys)),
    'limit': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'last': fields.Function(deserialize = lambda x: deserialize_query_last(x, allowed_snv_sort_keys))
}


@bp.route('/region/snv', methods=['GET'])
@parser.use_args(region_snv_argmap, location='query', validate=validate_paging_args)
def get_region_snv(args):
    args['limit'] = args.get('limit', current_app.config['BRAVO_API_PAGE_LIMIT'])  # Bad hack
    filter = { key: args[key] for  key in [ 'filter', 'allele_freq', 'annotation', 'cadd_phred', 'rsids' ] if key in args }
    result = variants.get_region_snv(args['chrom'], args['start'], args['stop'], filter, args.get('sort', []), args.get('last', {}), args['limit'])
    url = None
    if result['last'] is not None:
        url = request.base_url + '?' + '&'.join(f'{arg}={value}' for arg, value in request.args.items(True) if arg != 'last' and arg != 'sort')
        url += '&sort=' + ','.join(f'{key}:{direction}' for key, direction in result['sort'])
        url += f'&last=' + urllib.parse.quote(json.dumps(result['last']))
    response = make_response(jsonify({ 'data': result['data'], 'total': result['total'], 'limit': result['limit'], 'next': url, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


gene_argmap = {
    'name': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'allele_freq': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'annotation.gene.lof': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'annotation.gene.consequence': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'cadd_phred': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'rsids': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'sort': fields.Function(deserialize = lambda x: deserialize_query_sort(x, allowed_snv_sort_keys)),
    'introns': fields.Bool(required = False, missing = True),
    'limit': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'last': fields.Function(deserialize = lambda x: deserialize_query_last(x, allowed_snv_sort_keys))
}


@bp.route('/gene/snv', methods=['GET'])
@parser.use_args(gene_argmap, location='query', validate=validate_paging_args)
def get_gene_snv(args):
    return(get_gene_snv_impl(args))


# Implementation decoupled from arg parsing decorators
def get_gene_snv_impl(args):
    args['limit'] = args.get('limit', current_app.config['BRAVO_API_PAGE_LIMIT'])  # Bad hack
    filter = { key: args[key] for  key in [ 'filter', 'allele_freq', 'annotation', 'cadd_phred', 'rsids' ] if key in args }
    result = variants.get_gene_snv(args['name'], filter, args.get('sort', []), args.get('last', {}), args['limit'], args['introns'])
    url = None
    if result['last'] is not None:
        url = request.base_url + '?' + '&'.join(f'{arg}={value}' for arg, value in request.args.items(True) if arg != 'last' and arg != 'sort')
        url += '&sort=' + ','.join(f'{key}:{direction}' for key, direction in result['sort'])
        url += f'&last=' + urllib.parse.quote(json.dumps(result['last']))
    response = make_response(jsonify({ 'data': result['data'], 'total': result['total'], 'limit': result['limit'], 'next': url, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


@bp.route('/snv/filters', methods=['GET'])
def get_snv_filters():
    data = variants.get_snv_filters()
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


region_hist_argmap = {
    'chrom': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required = True, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than or equal to 0.'}),
    'stop': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'windows': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'allele_freq': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'annotation.region.lof': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'annotation.region.consequence': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'cadd_phred': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'rsids': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
}


@bp.route('/region/snv/histogram', methods=['GET'])
@parser.use_args(region_hist_argmap, location='query', validate=validate_paging_args)
def get_region_snv_histogram(args):
    filter = { key: args[key] for  key in [ 'filter', 'allele_freq', 'annotation', 'cadd_phred', 'rsids' ] if key in args }
    data = variants.get_region_snv_histogram(args['chrom'], args['start'], args['stop'], filter, args['windows'])
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


region_summary_argmap = {
    'chrom': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required = True, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than or equal to 0.'}),
    'stop': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'allele_freq': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'annotation.region.lof': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'annotation.region.consequence': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'cadd_phred': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'rsids': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
}


@bp.route('/region/snv/summary', methods=['GET'])
@parser.use_args(region_summary_argmap, location='query', validate=validate_paging_args)
def get_region_snv_summary(args):
    filter = { key: args[key] for  key in [ 'filter', 'allele_freq', 'annotation', 'cadd_phred', 'rsids' ] if key in args }
    data = variants.get_region_snv_summary(args['chrom'], args['start'], args['stop'], filter)
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


gene_snv_histogram_argmap = {
    'name': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'windows': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'allele_freq': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'annotation.gene.lof': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'annotation.gene.consequence': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'cadd_phred': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'rsids': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'introns': fields.Bool(required = False, missing = True)
}


@bp.route('/gene/snv/histogram', methods=['GET'])
@parser.use_args(gene_snv_histogram_argmap, location='query', validate=validate_paging_args)
def get_gene_snv_histogram(args):
    filter = { key: args[key] for  key in [ 'filter', 'allele_freq', 'annotation', 'cadd_phred', 'rsids' ] if key in args }
    data = variants.get_gene_snv_histogram(args['name'], filter, args['windows'], args['introns'])
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


gene_snv_summary_argmap = {
    'name': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'filter': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'allele_freq': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'annotation.gene.lof': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'annotation.gene.consequence': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'cadd_phred': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, float))),
    'rsids': fields.List(fields.Function(deserialize = lambda x: deserialize_query_filter(x, str))),
    'introns': fields.Bool(required = False, missing = True)
}


@bp.route('/gene/snv/summary', methods=['GET'])
@parser.use_args(gene_snv_summary_argmap, location='query', validate=validate_paging_args)
def get_gene_snv_summary(args):
    filter = { key: args[key] for  key in [ 'filter', 'allele_freq', 'annotation', 'cadd_phred', 'rsids' ] if key in args }
    data = variants.get_gene_snv_summary(args['name'], filter, args['introns'])
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


gene_argmap = {
    'name': fields.Str(required = False, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'chrom': fields.Str(required = False, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required = False, validate = lambda x: x >= 0, error_messages = {'validator_failed': 'Value must be greater than or equal to 0.'}),
    'stop': fields.Int(required = False, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'full': fields.Bool(required = False, missing = False)
}


@bp.route('/genes', methods=['GET'])
@parser.use_args(gene_argmap, location='query', validate=validate_paging_args)
def get_genes(args):
    data = []
    if 'name' in args:
        for gene in variants.get_genes(args['name'], args['full']):
            data.append(gene)
    elif all(x in args for x in ['chrom', 'start', 'stop']):
        for gene in variants.get_genes_in_region(args['chrom'], args['start'], args['stop'], args['full']):
            data.append(gene)
    else:
        raise UserError('Invalid query parameters')
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


qc_argmap = {
    'name': fields.Str(required = False, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'})
}


@bp.route('/qc', methods=['GET'])
@parser.use_args(qc_argmap, location='query', validate=validate_paging_args)
def get_qc(args):
    data = qc_metrics.get_metrics(args.get('name', None))
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


seq_summary_argmap = {
    'variant_id': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'})
}


@bp.route('/sequence/summary', methods=['GET'])
@parser.use_args(seq_summary_argmap, location='query', validate=validate_paging_args)
def get_sequence_summary(args):
    data = sequences.get_info(args['variant_id'])
    response = make_response(jsonify({ 'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None }), 200)
    response.mimetype = 'application/json'
    return response


sequence_argmap = {
    'variant_id': fields.Str(required = True, validate = lambda x: len(x) > 0, error_messages = {'validator_failed': 'Value must be a non-empty string.'}),
    'sample_no': fields.Int(required = True, validate = lambda x: x > 0, error_messages = {'validator_failed': 'Value must be greater than 0.'}),
    'heterozygous': fields.Bool(required = True),
    'index': fields.Bool(required = False, missing = False)
}


@bp.route('/sequence', methods=['GET'])
@parser.use_args(sequence_argmap, location='query', validate=validate_paging_args)
def get_sequence(args):
    if not args['index']:
        range_header = request.headers.get('Range', None)
        start = None
        stop = None
        if range_header:
            m = re.search(r'(\d+)-(\d*)', range_header)
            if m:
                start = int(m.group(1))
                stop = int(m.group(2))
        result = sequences.get_cram(args['variant_id'], args['sample_no'], args['heterozygous'], start, stop)
        if result is None:
            abort(500)
        response = make_response(result['file_bytes'], 206)
        response.headers['Content-Range'] = f'bytes {result["start_byte"]}-{result["stop_byte"]}/{result["file_size"]}'
        response.mimetype = 'application/octet-stream'
        response.direct_passthrough = True
    else:
        result = sequences.get_crai(args['variant_id'], args['sample_no'], args['heterozygous'])
        if result is None:
            abort(500)
        response = make_response(send_file(result, as_attachment = False))
    return response
