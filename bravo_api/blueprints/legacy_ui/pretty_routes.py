from flask import current_app, Blueprint, redirect, request, make_response, jsonify
from flask_cors import CORS
from webargs.flaskparser import use_kwargs
from webargs import fields, ValidationError
from bravo_api import api
from bravo_api.blueprints.legacy_ui import pretty_api

from marshmallow import validate

# For debugging
# from icecream import ic
# import pdb

# This blueprint should be mounted under a non-root route this duplicates some base api routes.
bp = Blueprint('pretty_routes', __name__)
CORS(bp)

ERR_EMPTY_MSG = {'validator_failed': 'Value must be a non-empty string.'}
ERR_GT_ZERO_MSG = {'validator_failed': 'Value must be greater than 0.'}

variant_argmap = {
    'variant_id': fields.Str(required=True, validate=validate.Length(min=1),
                             error_messages=ERR_EMPTY_MSG)
}


def validate_paging_args(parsed_args):
    if 'start' in parsed_args and 'stop' in parsed_args:
        if parsed_args['start'] >= parsed_args['stop']:
            raise ValidationError({'start': ['Start position must be greater than stop position.']})
    if 'limit' in parsed_args:
        if parsed_args['limit'] > current_app.config['BRAVO_API_PAGE_LIMIT']:
            raise ValidationError({'limit': [f'Page limit must be less than or equal to {current_app.config["BRAVO_API_PAGE_LIMIT"]}']})
    return True


@bp.route('/variant/api/snv/<string:variant_id>')
@use_kwargs(variant_argmap, location='view_args')
def variant(variant_id):
    args = {'variant_id': variant_id, 'full': 1}
    return api.get_variant(args)


@bp.route('/variant/api/snv/cram/summary/<string:variant_id>')
@use_kwargs(variant_argmap, location='view_args')
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
@use_kwargs(variant_cram_argmap, location='view_args')
def variant_cram(variant_id, sample_het, sample_no):
    args = {'variant_id': variant_id, 'sample_no': sample_no,
            'heterozygous': sample_het, 'index': 0}
    # The request header, will still be accessible from get_sequence
    response = api.get_sequence(args)
    return response


@bp.route('/variant/api/snv/crai/<string:variant_id>-<int:sample_het>-<int:sample_no>')
@use_kwargs(variant_cram_argmap, location='view_args')
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


genes_argmap = {
    'chrom': fields.Str(required=True, validate=validate.Length(min=1),
                        error_messages=ERR_EMPTY_MSG),
    'start': fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages=ERR_GT_ZERO_MSG),
    'stop': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG)
}


@bp.route('/genes/<string:chrom>-<int:start>-<int:stop>')
@use_kwargs(genes_argmap, location='view_args')
def genes(chrom, start, stop):
    args = {'chrom': chrom, 'start': start, 'stop': stop, 'full': 1}
    response = api.get_genes(args)
    return response


genes_name_argmap = {
    'name': fields.Str(required=True, validate=validate.Length(min=1),
                       error_messages=ERR_EMPTY_MSG)
}


@bp.route('/genes/api/<string:name>')
@use_kwargs(genes_name_argmap, location='view_args')
def genes_by_name(name):
    result = pretty_api.get_genes_by_name(name)

    response = make_response(jsonify(result), 200)
    response.mimetype = 'application/json'
    return response


coverage_view_argmap = {
    'chrom': fields.Str(required=True, validate=validate.Length(min=1),
                        error_messages=ERR_EMPTY_MSG),
    'start': fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages=ERR_GT_ZERO_MSG),
    'stop': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG)
}


coverage_json_argmap = {
    'size': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages=ERR_GT_ZERO_MSG),
    'next': fields.Str(required=True, allow_none=True, validate=validate.Length(min=1),
                       error_messages=ERR_EMPTY_MSG),
    'continue_from': fields.Int(required=False, validate=validate.Range(min=1),
                                error_messages=ERR_GT_ZERO_MSG),
}


@bp.route('/coverage/<string:chrom>-<int:start>-<int:stop>', methods=['POST'])
@use_kwargs(coverage_view_argmap, location='view_args')
@use_kwargs(coverage_json_argmap, location='json', validate=validate_paging_args)
def coverage(chrom, start, stop, size, next, continue_from=0):
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


# Functionally, this is only routes to /region/snv/histogram
#   Possible a stub for subsequent functionality?
@bp.route(('/variants/region/<string:variants_type>/'
           '<string:chrom>-<int:start>-<int:stop>/histogram'), methods=['POST', 'GET'])
def region_variants_histogram(variants_type, chrom, start, stop):
    args = {'chrom': chrom, 'start': start, 'stop': stop}

    if request.method == 'POST' and request.get_json():
        params = request.get_json()
        args.update(parse_filters_to_args(params.get('filters', [])))

        if 'windows' in params:
            args['windows'] = params["windows"]

    return api.get_region_snv_histogram(args)


# Functionally, this is only routes to /region/snv/summary
#   Possible a stub for subsequent functionality?
@bp.route('/variants/region/<string:variants_type>/<string:chrom>-<int:start>-<int:stop>/summary',
          methods=['POST', 'GET'])
def region_variants_summary(variants_type, chrom, start, stop):
    args = {'chrom': chrom, 'start': start, 'stop': stop}

    if request.method == 'POST' and request.get_json():
        params = request.get_json()
        args.update(parse_filters_to_args(params.get('filters', [])))

    return api.get_region_snv_summary(args)


gene_snv_summary_view_argmap = {
    'ensemble_id': fields.Str(required=True,
                              validate=lambda x: len(x) > 0,
                              error_messages=ERR_EMPTY_MSG)
}

gene_snv_summary_json_argmap = {
    'filters': fields.List(fields.Dict(), required=False, missing=[]),
    'introns': fields.Bool(required=False, missing=True)
}


@bp.route('/variants/gene/<string:ensemble_id>/summary', methods=['POST', 'GET'])
@use_kwargs(gene_snv_summary_view_argmap, location='view_args')
@use_kwargs(gene_snv_summary_json_argmap, location='json')
def gene_variants_summary(ensemble_id, introns, **kwargs):
    filter_arg_names = ['filter', 'allele_freq', 'annotation.gene.lof',
                        'annotation.gene.consequence', 'cadd_phred', 'rsids']
    filters = {key: kwargs[key] for key in filter_arg_names if key in kwargs}

    data = variants.get_gene_snv_summary(ensemble_id, filters, introns)
    response = make_response(jsonify({'data': data, 'total': len(data), 'limit': None,
                                      'next': None, 'error': None}), 200)
    response.mimetype = 'application/json'
    return response



# Functionally, this is only routes to /gene/snv/histogram
#   Possible a stub for subsequent functionality?
@bp.route('/variants/gene/<string:variants_type>/<string:gene_name>/histogram',
          methods=['POST', 'GET'])
def gene_variants_histogram(variants_type, gene_name):
    args = {'name': gene_name}

    if request.method == 'POST' and request.get_json():
        params = request.get_json()
        args.update(parse_filters_to_args(params.get('filters', [])))

        if 'introns' in params:
            args['introns'] = params['introns']
        if 'windows' in params:
            args['windows'] = params["windows"]

    return api.get_gene_snv_histogram(args)


# Could map to /region/snv or /region/sv
@bp.route('/variants/region/<string:variants_type>/<string:chrom>-<int:start>-<int:stop>',
          methods=['POST', 'GET'])
def variants(variants_type, chrom, start, stop):
    args = {'chrom': chrom, 'start': start, 'stop': stop}

    if request.method == 'POST' and request.get_json():
        params = request.get_json()
        if 'next' in params and params['next'] is not None:
            # try using redirect, but verify the UI doesn't choke on this.
            return redirect(params['next'], 303)

        args.update(parse_filters_to_args(params.get('filters', [])))

        for s in params.get('sorters', []):
            args['sort'] = ','.join(f'{s["field"]}:{s["dir"]}')
        if 'size' in params:
            args['limit'] = params['size']

    if variants_type == 'sv':
        return api.get_region(args)
    else:
        return api.get_region_snv(args)


# Functionally, this is only routes to /gene/snv
#   Possible a stub for subsequent functionality?
@bp.route('/variants/gene/<string:variants_type>/<string:gene_name>', methods=['POST', 'GET'])
def gene_variants(variants_type, gene_name):
    args = {'name': gene_name}

    if request.method == 'POST' and request.get_json():
        params = request.get_json()
        if 'next' in params and params['next'] is not None:
            # try using redirect, but verify the UI doesn't choke on this.
            return redirect(params['next'], 303)

        args.update(parse_filters_to_args(params.get('filters', [])))

        if 'size' in params:
            args['limit'] = params['size']
        if 'introns' in params:
            args['introns'] = params['introns']
        for s in params.get('sorters', []):
            args['sort'] = ','.join(f'{s["field"]}:{s["dir"]}')

    return api.get_gene_snv_impl(args)
