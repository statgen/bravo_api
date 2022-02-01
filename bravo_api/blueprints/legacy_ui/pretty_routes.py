"""@package Bravo Pretty Routes
Primary responsibilities are:
    - Consuming arguments from UI
    - Providing routes that use view arguments
    - Wrapping data in web responses.
"""
from flask import current_app, Blueprint, redirect, request, make_response, jsonify
from flask_cors import CORS
from webargs.flaskparser import FlaskParser
from webargs import fields, ValidationError
from marshmallow import EXCLUDE, validate
from bravo_api import api
from bravo_api.blueprints.legacy_ui import pretty_api


class Parser(FlaskParser):
    # Exclude extra parameters passed in json bodies.
    #   Accomodate extraneous pagination args from BraVue.
    DEFAULT_UNKNOWN_BY_LOCATION = {"json": EXCLUDE}


# This blueprint should be mounted under a non-root route this duplicates some base api routes.
bp = Blueprint('pretty_routes', __name__)
CORS(bp)


parser = Parser()

ERR_EMPTY_MSG = {'invalid_string': 'String must not be empty.'}
ERR_GT_ZERO_MSG = {'invalid_value': 'Value must be greater than 0.'}
ERR_START_STOP_MSG = {'invalid_start_stop': 'Start value must be less than stop value.'}

# Common arguements for chromosome region
region_argmap = {
    'chrom': fields.Str(required=True, validate=validate.Length(min=1),
                        error_messages=ERR_EMPTY_MSG),
    'start': fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages=ERR_GT_ZERO_MSG),
    'stop': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG)
}

variant_argmap = {
    'variant_id': fields.Str(required=True, validate=validate.Length(min=1),
                             error_messages=ERR_EMPTY_MSG)
}


def validate_region_args(parsed_args):
    if 'start' in parsed_args and 'stop' in parsed_args:
        if parsed_args['start'] >= parsed_args['stop']:
            raise ValidationError(ERR_START_STOP_MSG)
    return True


@bp.route('/variant/api/snv/<string:variant_id>')
@parser.use_kwargs(variant_argmap, location='view_args')
def variant(variant_id):
    args = {'variant_id': variant_id, 'full': 1}
    return api.get_variant(args)


@bp.route('/variant/api/snv/cram/summary/<string:variant_id>')
@parser.use_kwargs(variant_argmap, location='view_args')
def variant_cram_info(variant_id):
    args = {'variant_id': variant_id, 'full': 1}
    return api.get_sequence_summary(args)


variant_cram_argmap = {
    'variant_id': fields.Str(required=True, validate=validate.Length(min=1),
                             error_messages=ERR_EMPTY_MSG),
    'sample_het': fields.Bool(required=True),
    'sample_no': fields.Int(required=True, validate=validate.Range(min=1),
                            error_messages=ERR_GT_ZERO_MSG)
}


@bp.route('/variant/api/snv/cram/<string:variant_id>-<int:sample_het>-<int:sample_no>')
@parser.use_kwargs(variant_cram_argmap, location='view_args')
def variant_cram(variant_id, sample_het, sample_no):
    args = {'variant_id': variant_id, 'sample_no': sample_no,
            'heterozygous': sample_het, 'index': 0}
    # The request header, will still be accessible from get_sequence
    response = api.get_sequence(args)
    return response


@bp.route('/variant/api/snv/crai/<string:variant_id>-<int:sample_het>-<int:sample_no>')
@parser.use_kwargs(variant_cram_argmap, location='view_args')
def variant_crai(variant_id, sample_het, sample_no):
    args = {'variant_id': variant_id, 'sample_no': sample_no,
            'heterozygous': sample_het, 'index': 1}

    response = api.get_sequence(args)
    return response


@bp.route('/qc/api')
def qc():
    args = {}
    response = api.get_qc(args)
    return response


@bp.route('/genes/<string:chrom>-<int:start>-<int:stop>')
@parser.use_kwargs(region_argmap, location='view_args', validate=validate_region_args)
def genes(chrom, start, stop):
    result = pretty_api.get_genes_in_region(chrom, start, stop)
    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return response


coverage_json_argmap = {
    'size': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG),
    'next': fields.Str(required=True, allow_none=True, validate=validate.Length(min=1),
                       error_messages=ERR_EMPTY_MSG),
    'continue_from': fields.Int(required=False, validate=validate.Range(min=1),
                                error_messages=ERR_GT_ZERO_MSG, missing=0),
}


@bp.route('/coverage/<string:chrom>-<int:start>-<int:stop>', methods=['POST'])
@parser.use_kwargs(region_argmap, location='view_args', validate=validate_region_args)
@parser.use_kwargs(coverage_json_argmap, location='json')
def coverage(chrom, start, stop, size, next, continue_from):
    if size > current_app.config['BRAVO_API_PAGE_LIMIT']:
        size = current_app.config['BRAVO_API_PAGE_LIMIT']

    result = pretty_api.get_coverage(chrom, start, stop, size, continue_from)
    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return response


# Functionally, this can only route to /snv/filters.
#   Possible a stub for subsequent functionality?
@bp.route('/variants/<string:variants_type>', methods=['POST', 'GET'])
def variants_meta(variants_type):
    return api.get_snv_filters()


def parse_filters_to_args(filters):
    args = {}
    filter_type = {
       '=': 'eq',
       '!=': 'ne',
       '<': 'lt',
       '>': 'gt',
       '<=': 'lte',
       '>=': 'gte'
    }
    for item in filters:
        if isinstance(item, list):
            concat_vals = ','.join(f'{filter_type.get(subitem["type"], "eq")}:{subitem["value"]}'
                                   for subitem in item)
            args[item[0]['field']] = concat_vals
        else:
            args[item['field']] = f'{filter_type.get(item["type"], "eq")}:{item["value"]}'
    return(args)


region_snv_histogram_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'windows': fields.Int(required=True, validate=lambda x: x > 0,
                          error_messages=ERR_GT_ZERO_MSG)
}


@bp.route(('/variants/region/snv/'
           '<string:chrom>-<int:start>-<int:stop>/histogram'), methods=['POST', 'GET'])
@parser.use_kwargs(region_argmap, location='view_args', validate=validate_region_args)
@parser.use_kwargs(region_snv_histogram_json_argmap, location='json')
def region_variants_histogram(chrom, start, stop, filters, windows):
    data = pretty_api.get_region_snv_histogram(chrom, start, stop, filters, windows)

    response = make_response(jsonify({'data': data, 'total': len(data), 'limit': None,
                                      'next': None, 'error': None}), 200)
    response.mimetype = 'application/json'
    return response


region_snv_summary_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
}


@bp.route('/variants/region/snv/<string:chrom>-<int:start>-<int:stop>/summary',
          methods=['POST', 'GET'])
@parser.use_kwargs(region_argmap, location='view_args', validate=validate_region_args)
@parser.use_kwargs(region_snv_summary_json_argmap, location='json')
def region_variants_summary(chrom, start, stop, filters):
    data = pretty_api.get_region_snv_summary(chrom, start, stop, filters)
    response = make_response(jsonify({'data': data, 'total': len(data), 'limit': None,
                                      'next': None, 'error': None}), 200)
    response.mimetype = 'application/json'
    return response


region_snv_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'sorters': fields.List(fields.Dict(), required=False, missing=[]),
    'size': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG),
    'next': fields.Dict(required=True, allow_none=True, error_messages=ERR_EMPTY_MSG)
}


@bp.route('/variants/region/snv/<string:chrom>-<int:start>-<int:stop>',
          methods=['POST', 'GET'])
@parser.use_kwargs(region_argmap, location='view_args', validate=validate_region_args)
@parser.use_kwargs(region_snv_json_argmap, location='json')
def region_variants(chrom, start, stop, filters, sorters, size, next):
    if size > current_app.config['BRAVO_API_PAGE_LIMIT']:
        size = current_app.config['BRAVO_API_PAGE_LIMIT']

    result = pretty_api.get_region_snv(chrom, start, stop, filters, sorters, continue_from=next,
                                     limit=size)

    return make_response(jsonify(result), 200)
