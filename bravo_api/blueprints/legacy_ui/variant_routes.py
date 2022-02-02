"""@package Bravo Variant Routes
Provide convenient endpoints for variant queries.
Primary responsibilities are:
    - Consuming arguments from UI
    - Providing routes that use view arguments
    - Wrapping data in web responses.
"""
from flask import Blueprint, make_response, jsonify, send_file, abort, request
from flask_cors import CORS
from webargs import fields
from marshmallow import validate
from bravo_api.blueprints.legacy_ui import pretty_api, common
import re

# This blueprint should be mounted under a non-root route this duplicates some base api routes.
bp = Blueprint('variant_routes', __name__)
CORS(bp)

parser = common.Parser()


@bp.route('/qc/api')
def qc():
    result = pretty_api.get_qc()

    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return(response)


variant_argmap = {
    'variant_id': fields.Str(required=True, validate=validate.Length(min=1),
                             error_messages=common.ERR_EMPTY_MSG)
}


@bp.route('/variant/api/snv/<string:variant_id>')
@parser.use_kwargs(variant_argmap, location='view_args')
def variant(variant_id):
    result = pretty_api.get_variant(variant_id)

    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return(response)


@bp.route('/variant/api/snv/cram/summary/<string:variant_id>')
@parser.use_kwargs(variant_argmap, location='view_args')
def variant_cram_info(variant_id):
    result = pretty_api.get_variant_cram_info(variant_id)

    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return(response)


variant_cram_argmap = {
    'variant_id': fields.Str(required=True, validate=validate.Length(min=1),
                             error_messages=common.ERR_EMPTY_MSG),
    'sample_no': fields.Int(required=True, validate=validate.Range(min=1),
                            error_messages=common.ERR_GT_ZERO_MSG),
    'sample_het': fields.Bool(required=True)
}


@bp.route('/variant/api/snv/cram/<string:variant_id>-<int:sample_het>-<int:sample_no>')
@parser.use_kwargs(variant_cram_argmap, location='view_args')
def variant_cram(variant_id, sample_het, sample_no):
    range_header = request.headers.get('Range', None)
    start = None
    stop = None
    if range_header:
        m = re.search(r'(\d+)-(\d*)', range_header)
        if m:
            start = int(m.group(1))
            stop = int(m.group(2))

    result = pretty_api.get_variant_cram(variant_id, sample_het, sample_no, start, stop)
    if result is None:
        print(f'start: {start} stop: {stop}')
        abort(404)

    response = make_response(result['file_bytes'], 206)
    response.headers['Content-Range'] = f'bytes {result["start_byte"]}-{result["stop_byte"]}/{result["file_size"]}'
    response.mimetype = 'application/octet-stream'
    response.direct_passthrough = True

    return(response)


@bp.route('/variant/api/snv/crai/<string:variant_id>-<int:sample_het>-<int:sample_no>')
@parser.use_kwargs(variant_cram_argmap, location='view_args')
def variant_crai(variant_id, sample_no, sample_het):
    result = pretty_api.get_variant_crai(variant_id, sample_no, sample_het)
    if result is None:
        abort(404)
    response = make_response(send_file(result, as_attachment=False))
    return response
