from bravo_api.blueprints.legacy_ui import pretty_routes
from flask import Flask, make_response, jsonify
from icecream import ic

app = Flask('dummy')
app.register_blueprint(pretty_routes.bp)


def mock_json_response(args):
    response = make_response(jsonify({'data': 'test'}), 200)
    response.mimetype = 'application/json'
    return response


def mock_response_echo_request_headers(args):
    response = make_response(jsonify({'data': 'test'}), 200)
    response.mimetype = 'application/json'
    return response


def test_variant_id_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_variant', side_effect=mock_json_response)

    variant_id = 'rs12345678'
    expected_args = {'variant_id': variant_id, 'full': 1}

    with app.test_client() as client:
        client.get('/variant/api/snv/rs12345678')
    mock.assert_called_with(expected_args)


def test_variant_cram_info_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_sequence_summary', side_effect=mock_json_response)

    variant_id = 'rs12345678'
    expected_args = {'variant_id': variant_id, 'full': 1}

    with app.test_client() as client:
        client.get('/variant/api/snv/cram/summary/' + variant_id)
    mock.assert_called_with(expected_args)


def test_variant_cram_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_sequence', side_effect=mock_json_response)

    variant_id = 'rs12345678'
    sample_het = 1
    sample_no = 10

    expected_args = {'variant_id': variant_id, 'sample_no': sample_no,
                     'heterozygous': 1, 'index': 0}

    with app.test_client() as client:
        client.get(f'/variant/api/snv/cram/{variant_id}-{sample_het}-{sample_no}')
    mock.assert_called_with(expected_args)


def test_variant_crai_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_sequence', side_effect=mock_json_response)

    variant_id = 'rs12345678'
    sample_het = 1
    sample_no = 10

    expected_args = {'variant_id': variant_id, 'sample_no': sample_no,
                     'heterozygous': sample_het, 'index': 1}

    with app.test_client() as client:
        client.get(f'/variant/api/snv/crai/{variant_id}-{sample_het}-{sample_no}')
    mock.assert_called_with(expected_args)


def test_qc_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_qc', side_effect=mock_json_response)
    expected_args = {}

    with app.test_client() as client:
        client.get('/qc/api')
    mock.assert_called_with(expected_args)


def test_genes_range_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_genes', side_effect=mock_json_response)

    chrom = '11'
    start = 500000
    stop = 5001000

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop, 'full': 1}

    with app.test_client() as client:
        client.get(f'/genes/{chrom}-{start}-{stop}')
    mock.assert_called_with(expected_args)


def test_genes_name_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_genes', side_effect=mock_json_response)

    name = 'foo'
    expected_args = {'name': name, 'full': 1}

    with app.test_client() as client:
        client.get(f'/genes/api/{name}')
    mock.assert_called_with(expected_args)


def test_coverage_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_coverage', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # body args
    size = 100
    next = None

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop, 'limit': size}

    with app.test_client() as client:
        client.post(f'/coverage/{chrom}-{start}-{stop}', json={'size': size, 'next': next})
    mock.assert_called_with(expected_args)


def test_coverage_redirect(mocker):
    mocker.patch('bravo_api.api.get_coverage', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # body args
    size = 100
    next = 'https://www.example.com/foo'

    with app.test_client() as client:
        resp = client.post(f'/coverage/{chrom}-{start}-{stop}',
                           json={'size': size, 'next': next},
                           follow_redirects=False)
    assert resp.status_code == 303
    assert resp.location == next


def test_variants_meta_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_coverage', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # body args
    size = 100
    next = None

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop, 'limit': size}

    with app.test_client() as client:
        client.post(f'/coverage/{chrom}-{start}-{stop}', json={'size': size, 'next': next})
    mock.assert_called_with(expected_args)


def test_region_histogram_arg_parsing():
    # Valid filter examples
    filters1 = [{'field': 'filter', 'type': '=', 'value': 'PASS'}]
    filters2 = [{'field': 'filter', 'type': '=', 'value': 'PASS'},
                {'field': 'annotation.gene.consequence',
                'type': '=', 'value': 'frameshift_variant'}]
    filters3 = [{'field': 'filter', 'type': '=', 'value': 'PASS'},
                {'field': 'annotation.gene.consequence',
                 'type': '=', 'value': 'frameshift_variant'},
                {'field': 'annotation.gene.consequence',
                 'type': '=', 'value': 'synonymous_variant'},
                {'field': 'annotation.gene.lof', 'type': '=', 'value': 'HC'},
                {'field': 'annotation.gene.lof', 'type': '=', 'value': 'LC'}]
    # Allele frequency is the list of lists case.
    filters4 = [[{"field": "allele_freq", "type": ">", "value": 0.01},
                 {"field": "allele_freq", "type": "<", "value": 0.99}]]
    filters5 = [{"field": "filter", "type": "=", "value": "PASS"},
                [{"field": "allele_freq", "type": ">", "value": 0.01},
                 {"field": "allele_freq", "type": "<", "value": 0.99}]]

    expected_args1 = {'filter': 'eq:PASS'}
    expected_args2 = {'annotation.gene.consequence': 'eq:frameshift_variant', 'filter': 'eq:PASS'}
    expected_args3 = {'annotation.gene.consequence': 'eq:synonymous_variant',
                      'annotation.gene.lof': 'eq:LC', 'filter': 'eq:PASS'}
    expected_args4 = {'allele_freq': 'gt:0.01,lt:0.99'}
    expected_args5 = {'allele_freq': 'gt:0.01,lt:0.99', 'filter': 'eq:PASS'}

    assert pretty_routes.parse_filters_to_args(filters1) == expected_args1
    assert pretty_routes.parse_filters_to_args(filters2) == expected_args2
    assert pretty_routes.parse_filters_to_args(filters3) == expected_args3
    assert pretty_routes.parse_filters_to_args(filters4) == expected_args4
    assert pretty_routes.parse_filters_to_args(filters5) == expected_args5


def test_region_histogram_post_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_region_snv_histogram', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # post body content
    body = {'filters': [{'field': 'filter', 'type': '=', 'value': 'PASS'},
                        [{'field': 'allele_freq', 'type': '>', 'value': 0.01},
                         {'field': 'allele_freq', 'type': '<', 'value': 0.99}]],
            'introns': True, 'windows': 550}

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop,
                     'allele_freq': 'gt:0.01,lt:0.99', 'filter': 'eq:PASS', 'windows': 550}

    with app.test_client() as client:
        client.post(f'/variants/region/snv/{chrom}-{start}-{stop}/histogram', json=body)

    mock.assert_called_with(expected_args)


def test_region_histogram_get_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_region_snv_histogram', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop}

    with app.test_client() as client:
        client.get(f'/variants/region/snv/{chrom}-{start}-{stop}/histogram')

    mock.assert_called_with(expected_args)
