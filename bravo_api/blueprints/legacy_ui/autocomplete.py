from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from bravo_api.models import variants

bp = Blueprint('autocomplete', __name__)
CORS(bp)


def search_gene_names(query):
    result = []
    for gene in variants.get_genes(query, False):
        result.append({
            'value': gene['gene_name'],
            'data': {
                'feature': 'gene',
                'chrom': gene['chrom'],
                'start': gene['start'],
                'stop': gene['stop'],
                'type': gene['gene_type']
            }
        })
    return(result)


def search_variant_ids(query):
    """Given query string, return array of dicts with value & data."""
    result = []
    if query.startswith('rs'):
        for variant in variants.get_snv(query, None, None, False):
            result.append({
                'value': [x for x in variant['rsids'] if x.startswith(query)][0],
                'data': {
                    'feature': 'snv',
                    'variant_id': variant['variant_id'],
                    'type': variant['annotation']['region']['consequence'][0]
                }
            })
    return(result)


def aggregate(query):
    gene_results = search_gene_names(query)

    if len(gene_results) < 10:
        variant_results = search_variant_ids(query)
    else:
        variant_results = []

    return({"suggestions": [*gene_results, *variant_results]})


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    results = aggregate(request.args.get('query', ''))
    return make_response(jsonify(results), 200)
