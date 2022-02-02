"""@package Bravo Region Routes
Provide convenient endpoints for chromosome region queries.
Primary responsibilities are:
    - Consuming arguments from UI
    - Providing routes that use view arguments
    - Wrapping data in web responses.
"""
from flask import current_app, Blueprint, make_response, jsonify
from flask_cors import CORS
from webargs import fields, ValidationError
from marshmallow import validate
from bravo_api.blueprints.legacy_ui import pretty_api, common

# This blueprint should be mounted under a non-root route this duplicates some base api routes.
bp = Blueprint('region_routes', __name__)
CORS(bp)

parser = common.Parser()

# Common arguements for chromosome region
region_argmap = {
    'chrom': fields.Str(required=True, validate=validate.Length(min=1),
                        error_messages=common.ERR_EMPTY_MSG),
    'start': fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages=common.ERR_GT_ZERO_MSG),
    'stop': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=common.ERR_GT_ZERO_MSG)
}


def validate_region_args(parsed_args):
    if parsed_args['start'] >= parsed_args['stop']:
        raise ValidationError(common.ERR_START_STOP_MSG)
    return True


@bp.route('/genes/<string:chrom>-<int:start>-<int:stop>')
@parser.use_kwargs(region_argmap, location='view_args', validate=validate_region_args)
def genes(chrom, start, stop):
    result = pretty_api.get_genes_in_region(chrom, start, stop)
    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return response


coverage_json_argmap = {
    'size': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=common.ERR_GT_ZERO_MSG),
    'next': fields.Str(required=True, allow_none=True, validate=validate.Length(min=1),
                       error_messages=common.ERR_EMPTY_MSG),
    'continue_from': fields.Int(required=False, validate=validate.Range(min=1),
                                error_messages=common.ERR_GT_ZERO_MSG, missing=0),
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


region_snv_histogram_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'windows': fields.Int(required=True, validate=lambda x: x > 0,
                          error_messages=common.ERR_GT_ZERO_MSG)
}


@bp.route(('/variants/region/snv/<string:chrom>-<int:start>-<int:stop>/histogram'),
          methods=['POST', 'GET'])
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
                       error_messages=common.ERR_GT_ZERO_MSG),
    'next': fields.Dict(required=True, allow_none=True, error_messages=common.ERR_EMPTY_MSG)
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
