"""@package Bravo Pretty Routes
Primary responsibilities are:
    - Consuming arguments from UI
    - Providing routes that use view arguments
    - Wrapping data in web responses.
"""
from flask import Blueprint
from flask_cors import CORS
from webargs import fields
from marshmallow import validate
from bravo_api import api
from bravo_api.blueprints.legacy_ui import pretty_api, common

# This blueprint should be mounted under a non-root route this duplicates some base api routes.
bp = Blueprint('pretty_routes', __name__)
CORS(bp)

parser = common.Parser()

variant_argmap = {
    'variant_id': fields.Str(required=True, validate=validate.Length(min=1),
                             error_messages=common.ERR_EMPTY_MSG)
}


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
                             error_messages=common.ERR_EMPTY_MSG),
    'sample_het': fields.Bool(required=True),
    'sample_no': fields.Int(required=True, validate=validate.Range(min=1),
                            error_messages=common.ERR_GT_ZERO_MSG)
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
