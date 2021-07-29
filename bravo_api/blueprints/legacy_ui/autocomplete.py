from flask import Blueprint, request, jsonify, make_response
from bravo_api.models import variants

bp = Blueprint('autocomplete', __name__)


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


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')

    gene_results = search_gene_names(query)

    if len(gene_results):
        variant_results = search_variant_ids(query)
    else:
        variant_results = []

    suggestions = gene_results.extend(variant_results)
    return make_response(jsonify({"suggestions": suggestions}), 200)
