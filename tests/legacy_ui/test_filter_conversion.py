from bravo_api.blueprints.legacy_ui import pretty_api


# process UI filters to internal api "user filters"
def test_munging_nesting_filters():
    filters = [
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'start_retained_variant'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'stop_retained_variant'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'synonymous_variant'}]

    expected_result = {'annotation': {'gene': {'consequence': [
        {'$eq': ['start_retained_variant']},
        {'$eq': ['stop_retained_variant']},
        {'$eq': ['synonymous_variant']}
    ]}}}

    result = pretty_api.munge_ui_filters(filters)
    assert(expected_result == result)


def test_munging_numeric_filters():
    filters = [{'field': 'allele_freq', 'type': '>', 'value': 0.001},
               {'field': 'allele_freq', 'type': '<', 'value': 0.98},
               {'field': 'cadd_phred', 'type': '>', 'value': 0.2},
               {'field': 'cadd_phred', 'type': '<', 'value': 66}]

    expected_result = {
        'allele_freq': [{'$gt': [0.001]}, {'$lt': [0.98]}],
        'cadd_phred': [{'$gt': [0.2]}, {'$lt': [66.0]}]
    }

    result = pretty_api.munge_ui_filters(filters)
    assert(expected_result == result)


def test_munging_quality_filters():
    filters = [{'field': 'filter', 'type': '=', 'value': 'PASS'},
               {'field': 'filter', 'type': '=', 'value': 'SVM'},
               {'field': 'filter', 'type': '=', 'value': 'DISC'},
               {'field': 'filter', 'type': '=', 'value': 'EXHET'}]

    expected_result = {
        'filter': [{'$eq': ['PASS']}, {'$eq': ['SVM']}, {'$eq': ['DISC']}, {'$eq': ['EXHET']}]
    }

    result = pretty_api.munge_ui_filters(filters)
    assert(expected_result == result)


def test_munging_mess_of_filters():
    filters = [
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'synonymous_variant'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'frameshift_variant'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'stop_lost'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'transcript_ablation'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'protein_altering_variant'},
        {'field': 'annotation.gene.consequence', 'type': '=', 'value': 'regulatory_region_variant'},
        {'field': 'filter', 'type': '=', 'value': 'PASS'},
        {'field': 'allele_freq', 'type': '>', 'value': 0.001},
        {'field': 'allele_freq', 'type': '<', 'value': 0.99}]

    expected_result = {
        'filter': [{'$eq': ['PASS']}],
        'allele_freq': [{'$gt': [0.001]}, {'$lt': [0.99]}],
        'annotation': {'gene': {'consequence': [
            {'$eq': ['synonymous_variant']},
            {'$eq': ['frameshift_variant']},
            {'$eq': ['stop_lost']},
            {'$eq': ['transcript_ablation']},
            {'$eq': ['protein_altering_variant']},
            {'$eq': ['regulatory_region_variant']}
            ]
        }}
    }

    result = pretty_api.munge_ui_filters(filters)
    assert(expected_result == result)
