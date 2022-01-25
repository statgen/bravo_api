from bravo_api.models import variants, coverage


def get_genes_by_name(name='', full=1):
    data = []
    for gene in variants.get_genes(name, full):
        data.append(gene)
    result = {'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None}
    return(result)


def get_genes_in_region(chrom, start, stop, full=1):
    data = []
    for gene in variants.get_genes_in_region(chrom, start, stop, full):
        data.append(gene)
    result = {'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None}
    return(result)


# continue_from replaces 'last' of previous versions.
def get_coverage(chrom, start, stop, limit, continue_from=None):
    cov = coverage.get_coverage(chrom, start, stop, limit, continue_from)

    continue_from = None
    if not cov['stop_reached']:
        continue_from = cov["last"]

    result = {'data': cov['data'], 'total': cov['total'], 'limit': limit,
              'next': continue_from, 'error': None}
    return result

    # if result['last'] is not None:
    #     url = request.base_url + '?' + '&'.join(f'{arg}={value}' for arg, value in request.args.items(True) if arg != 'last')
    #     url += f'&last={result["last"]}'

    # response = make_response(jsonify({ 'data': result['data'], 'total': result['total'], 'limit': args['limit'], 'next': continue_from, 'error': None }), 200)
    # response.mimetype = 'application/json'
    # return response
