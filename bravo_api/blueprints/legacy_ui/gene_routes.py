"""@package Bravo Gene Routes
Provide convenient endpoints for gene queries.
Primary responsibilities are:
    - Consuming arguments from UI
    - Providing routes that use view arguments
    - Wrapping data in web responses.
"""

from flask import current_app, Blueprint, make_response, jsonify
from flask_cors import CORS
from webargs.flaskparser import FlaskParser
from webargs import fields
from marshmallow import EXCLUDE, validate
from bravo_api.blueprints.legacy_ui import pretty_api


class Parser(FlaskParser):
    # Exclude extra parameters passed in json bodies.
    #   Accomodate extraneous pagination args from BraVue.
    DEFAULT_UNKNOWN_BY_LOCATION = {"json": EXCLUDE}


# This blueprint should be mounted under a non-root route this duplicates some base api routes.
bp = Blueprint('gene_routes', __name__)
CORS(bp)


parser = Parser()

ERR_EMPTY_MSG = {'validator_failed': 'Value must be a non-empty string.'}
ERR_GT_ZERO_MSG = {'validator_failed': 'Value must be greater than 0.'}

genes_name_argmap = {
    'name': fields.Str(required=True, validate=validate.Length(min=1),
                       error_messages=ERR_EMPTY_MSG)
}


@bp.route('/genes/api/<string:name>')
@parser.use_kwargs(genes_name_argmap, location='view_args')
def genes_by_name(name):
    result = pretty_api.get_genes_by_name(name)

    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return response


gene_snv_summary_view_argmap = {
    'ensembl_id': fields.Str(required=True,
                             validate=lambda x: len(x) > 0,
                             error_messages=ERR_EMPTY_MSG)
}

gene_snv_summary_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'introns': fields.Bool(required=False, missing=True)
}


@bp.route('/variants/gene/snv/<string:ensembl_id>/summary', methods=['POST', 'GET'])
@parser.use_kwargs(gene_snv_summary_view_argmap, location='view_args')
@parser.use_kwargs(gene_snv_summary_json_argmap, location='json')
def gene_variants_summary(ensembl_id, introns, filters):

    data = pretty_api.get_gene_snv_summary(ensembl_id, filters, introns)
    response = make_response(jsonify({'data': data, 'total': len(data), 'limit': None,
                                      'next': None, 'error': None}), 200)
    response.mimetype = 'application/json'
    return response


gene_snv_histogram_view_argmap = {
    'ensembl_id': fields.Str(required=True,
                             validate=lambda x: len(x) > 0,
                             error_messages=ERR_EMPTY_MSG)
}

gene_snv_histogram_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'introns': fields.Bool(required=False, missing=True),
    'windows': fields.Int(required=True, validate=lambda x: x > 0,
                          error_messages=ERR_GT_ZERO_MSG)
}


@bp.route('/variants/gene/snv/<string:ensembl_id>/histogram', methods=['POST', 'GET'])
@parser.use_kwargs(gene_snv_histogram_view_argmap, location='view_args')
@parser.use_kwargs(gene_snv_histogram_json_argmap, location='json')
def gene_variants_histogram(ensembl_id, filters, introns, windows=1000):
    data = pretty_api.get_gene_snv_histogram(ensembl_id, filters, windows, introns)

    response = make_response(jsonify({'data': data, 'total': len(data), 'limit': None,
                                      'next': None, 'error': None}), 200)
    response.mimetype = 'application/json'
    return response


gene_snv_view_argmap = {
    'ensembl_id': fields.Str(required=True,
                             validate=lambda x: len(x) > 0,
                             error_messages=ERR_EMPTY_MSG)
}

gene_snv_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'sorters': fields.List(fields.Dict(), required=False, missing=[]),
    'introns': fields.Bool(required=False, missing=True),
    'size': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG),
    'next': fields.Dict(required=True, allow_none=True, error_messages=ERR_EMPTY_MSG)
}


@bp.route('/variants/gene/snv/<string:ensembl_id>', methods=['POST', 'GET'])
@parser.use_kwargs(gene_snv_view_argmap, location='view_args')
@parser.use_kwargs(gene_snv_json_argmap, location='json')
def gene_variants(ensembl_id, filters, sorters, introns, size, next):
    if size > current_app.config['BRAVO_API_PAGE_LIMIT']:
        size = current_app.config['BRAVO_API_PAGE_LIMIT']

    result = pretty_api.get_gene_snv(ensembl_id, filters, sorters, continue_from=next,
                                     limit=size, introns=introns)

    return make_response(jsonify(result), 200)
