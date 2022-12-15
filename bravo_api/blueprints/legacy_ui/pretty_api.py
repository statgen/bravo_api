"""@package Bravo Pretty API
Two main responsibilities are:
    - Converting user facing args to underlying model calls.
    - Aggregate results to data structure expected by web serving layer.
"""
from bravo_api.models import variants, qc_metrics, sequences
from flask import current_app

FILTER_TYPE_MAPPING = {
    '=':  '$eq',
    '!=': '$ne',
    '<':  '$lt',
    '>':  '$gt',
    '<=': '$lte',
    '>=': '$gte'
}

ALLOWED_SNV_SORT_KEYS = [
   'pos',
   'filter',
   'qual',
   'variant_id',
   'allele_num',
   'allele_freq',
   'hom_count',
   'het_count',
   'cadd_phred',
   'rsids',
   'annotation.region.lof',
   'annotation.region.consequence',
   'annotation.gene.lof',
   'annotation.gene.consequence'
]

SORT_DIR_MAP = {"asc": "asc",
                1: "asc",
                "": "asc",
                None: "asc",
                "desc": "desc",
                -1: "desc"}


def munge_ui_sort(sort_list):
    """
    @param sort_list. List of dicts with field and dir keys.
    @return List of tuples in the form [(field, dir)]
    """
    user_sort = []

    for sort in sort_list:
        sort_field = sort.get('field')
        direction = sort.get('dir')

        if sort_field in ALLOWED_SNV_SORT_KEYS and direction in SORT_DIR_MAP:
            user_sort.append((sort_field, SORT_DIR_MAP[direction]))

    return(user_sort)


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


def chunked_coverage(chrom, start, stop, continue_from=0):
    """
    Chunked coverage. Heuristically break up request into chunks.
    """
    # TODO: determine bin and chunk size based on request length.
    act_bin = 'bin_0.50'
    act_chunk = 15_000

    act_start = max(start, continue_from)
    act_stop = min(stop, act_start + act_chunk)

    cov_data = current_app.coverage_provider.coverage(act_bin, chrom, act_start, act_stop)

    # Next request should continue beyond the last position in the returned data or act_stop
    if cov_data:
        last_data = cov_data[-1]
        last_data_pos = last_data.get('stop', 0)
    else:
        last_data_pos = 0

    next_pos = max(last_data_pos, act_stop) + 1

    result = {'coverage': cov_data, 'continue_from': next_pos}
    return result


def get_gene_snv_summary(ensembl_id, filters, introns):
    munged_filters = munge_ui_filters(filters)
    data = variants.get_gene_snv_summary(ensembl_id, munged_filters, introns)
    return(data)


def get_gene_snv_histogram(ensembl_id, filters, windows, introns):
    munged_filters = munge_ui_filters(filters)
    data = variants.get_gene_snv_histogram(ensembl_id, munged_filters, windows, introns)
    return(data)


def get_gene_snv(ensembl_id, filters, sorts, continue_from, limit, introns):
    munged_filters = munge_ui_filters(filters)
    munged_sorters = munge_ui_sort(sorts)

    snv = variants.get_gene_snv(ensembl_id, munged_filters, munged_sorters,
                                continue_from, limit, introns)

    return({'data': snv['data'], 'total': snv['total'], 'limit': snv['limit'],
            'next': snv['last'], 'error': None})


def get_region_snv_histogram(chrom, start, stop, filters, windows):
    munged_filters = munge_ui_filters(filters)
    data = variants.get_region_snv_histogram(chrom, start, stop, munged_filters, windows)
    return(data)


def get_region_snv(chrom, start, stop, filters, sorts, continue_from, limit):
    munged_filters = munge_ui_filters(filters)
    munged_sorters = munge_ui_sort(sorts)

    snv = variants.get_region_snv(chrom, start, stop, munged_filters, munged_sorters,
                                  continue_from, limit)

    return({'data': snv['data'], 'total': snv['total'], 'limit': snv['limit'],
            'next': snv['last'], 'error': None})


def get_region_snv_summary(chrom, start, stop, filters):
    munged_filters = munge_ui_filters(filters)
    data = variants.get_region_snv_summary(chrom, start, stop, munged_filters)
    return(data)


def get_qc():
    data = qc_metrics.get_metrics()
    return({'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None})


def get_snv_filters():
    data = variants.get_snv_filters()
    return({'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None})


def get_variant(variant_id):
    data = []
    for variant in variants.get_snv(variant_id, None, None, 1):
        data.append(variant)
    return({'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None})


def get_variant_cram_info(variant_id):
    data = sequences.get_info(variant_id)
    return({'data': data, 'total': len(data), 'limit': None, 'next': None, 'error': None})


def get_variant_crai(variant_id, sample_no, heterozygous):
    result = sequences.get_crai(variant_id, sample_no, heterozygous)
    return(result)


def get_variant_cram(variant_id, heterozygous, sample_no, start, stop):
    result = sequences.get_cram(variant_id, sample_no, heterozygous, start, stop)
    return(result)
