"""@package Bravo Pretty API
Two main responsibilities are:
    - Converting user facing args to underlying model calls.
    - Aggregate results to data structure expected by web serving layer.
"""
from bravo_api.models import variants, coverage


FILTER_TYPE_MAPPING = {
    '=':  '$eq',
    '!=': '$ne',
    '<':  '$lt',
    '>':  '$gt',
    '<=': '$lte',
    '>=': '$gte'
}


def convert_to_op_val(tipe, value):
    """
    @return list wrapping op: val dict to facilitate appending to list of op: val dicts.
    """
    op = FILTER_TYPE_MAPPING.get(tipe)
    val = [value]
    return([{op: val}])


def nest_dot_fields(op_filters):
    """
    Mutate op-val filters to apply nesting to field names that had dots in them.
    """
    nestable_keys = [key for key in op_filters if '.' in key]
    for key_to_nest in nestable_keys:
        # Remove key and store the op_vals from it
        op_vals = op_filters.pop(key_to_nest)
        levels = key_to_nest.split('.')
        # Begin with innermost level where op_vals will be stored
        nest = {levels.pop(): op_vals}
        # Remaining levels become more dict wrapping. Reverse to do inner to outer
        for level in reversed(levels):
            nest = {level: nest}
        # Add nest back to the op_filters.
        op_filters.update(nest)
    return(op_filters)


def munge_ui_filters(filters):
    """
    Take filters formatted by UI and produce user_filters suitable to pass to model functions.

    @param filters a list of dicts with keys field, type, and value
    @return dict keyed by the unique input field value with type and value aggregated to a list.
       {field1: [{op: [val]}, {op: [val]}, ...],
        field2: [{op: [val]}, {op: [val]}, ...],
        nested3:{ some3:{ field3: [{op: [val]}, {op: [val]}, ...]}}
       }
    """
    op_filters = {}
    for filt in filters:
        # Each field value in filters should be a key in the result
        op_val = op_filters.setdefault(filt['field'], [])
        # The corresponding type and value are appended the {op: val} list
        op_val += convert_to_op_val(filt['type'], filt['value'])

    # Mutate result to when nested fields are present.
    user_filters = nest_dot_fields(op_filters)

    return(user_filters)


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


def get_coverage(chrom, start, stop, limit, continue_from=None):
    cov = coverage.get_coverage(chrom, start, stop, limit, continue_from)

    if cov['stop_reached']:
        continue_from = None
    else:
        continue_from = cov["last"]

    result = {'data': cov['data'], 'total': cov['total'], 'limit': limit,
              'next': continue_from, 'error': None}
    return result


def get_gene_snv_summary(ensembl_id, filters, introns):
    munged_filters = munge_ui_filters(filters)
    data = variants.get_gene_snv_summary(ensembl_id, munged_filters, introns)
    return data
