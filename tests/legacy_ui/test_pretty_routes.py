from bravo_api.blueprints.legacy_ui import pretty_routes
from flask import Flask, make_response, jsonify
from icecream import ic

app = Flask('dummy')
app.register_blueprint(pretty_routes.bp)

def mock_get_genes_by_name(name):
    return({'data': [1,2,3], 'total': 3, 'limit': None, 'next': None, 'error': None})

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


def test_variant_crai_wild(mocker):
    mock = mocker.patch('bravo_api.api.get_sequence', side_effect=mock_json_response)
    expected_args = {'variant_id': '11-5225469-A-T', 'sample_no': 1,
                     'heterozygous': True, 'index': 1}

    with app.test_client() as client:
        resp = client.get(f'/variant/api/snv/crai/11-5225469-A-T-1-1')
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


def test_genes_by_name(mocker, client):
    mock = mocker.patch('bravo_api.blueprints.legacy_ui.pretty_api.get_genes_by_name',
                        side_effect=mock_get_genes_by_name)
    name = 'foo'
    with app.test_client() as client:
        resp = client.get(f'/genes/api/{name}')

    mock.assert_called_with(name)
    assert(resp.content_type == 'application/json')


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


def test_region_summary_post_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_region_snv_summary', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # post body content
    body = {'filters': [{'field': 'filter', 'type': '=', 'value': 'PASS'},
                        {'field': 'annotation.gene.consequence', 'type': '=',
                         'value': 'frameshift_variant'}],
            'introns': True}

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop,
                     'annotation.gene.consequence': 'eq:frameshift_variant', 'filter': 'eq:PASS'}

    with app.test_client() as client:
        client.post(f'/variants/region/snv/{chrom}-{start}-{stop}/summary', json=body)

    mock.assert_called_with(expected_args)


def test_region_summary_get_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_region_snv_summary', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop}

    with app.test_client() as client:
        client.get(f'/variants/region/snv/{chrom}-{start}-{stop}/summary')

    mock.assert_called_with(expected_args)


def test_gene_summary_post_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_gene_snv_summary', side_effect=mock_json_response)

    # path args
    name = 'ENSG00000244734'

    body = {'filters': [{'field': 'filter', 'type': '=', 'value': 'PASS'},
                        {'field': 'annotation.gene.consequence', 'type': '=',
                         'value': 'synonymous_variant'},
                        {'field': 'annotation.gene.lof', 'type': '=', 'value': 'HC'}],
            'introns': True}

    expected_args = {'name': name,
                     'annotation.gene.consequence': 'eq:synonymous_variant',
                     'annotation.gene.lof': 'eq:HC',
                     'filter': 'eq:PASS',
                     'introns': True}

    with app.test_client() as client:
        client.post(f'/variants/gene/snv/{name}/summary', json=body)

    mock.assert_called_with(expected_args)


def test_gene_summary_get_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_gene_snv_summary', side_effect=mock_json_response)

    # path args
    name = 'ENSG00000244734'

    expected_args = {'name': name}

    with app.test_client() as client:
        client.get(f'/variants/gene/snv/{name}/summary')

    mock.assert_called_with(expected_args)


def test_gene_histogram_post_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_gene_snv_histogram', side_effect=mock_json_response)

    # path args
    name = 'ENSG00000244734'
    # post body content
    body = {"filters": [{"field": "filter", "type": "=", "value": "PASS"}],
            "introns": True, "windows": 564}

    expected_args = {'name': name, 'filter': 'eq:PASS', 'windows': 564, 'introns': True}

    with app.test_client() as client:
        client.post(f'/variants/gene/snv/{name}/histogram', json=body)

    mock.assert_called_with(expected_args)


def test_gene_histogram_get_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_gene_snv_histogram', side_effect=mock_json_response)

    # path args
    name = 'ENSG00000244734'

    expected_args = {'name': name}

    with app.test_client() as client:
        client.get(f'/variants/gene/snv/{name}/histogram')

    mock.assert_called_with(expected_args)


def test_variants_redirect(mocker):
    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # body args
    size = 100
    next = 'https://www.example.com/foo'

    with app.test_client() as client:
        snv_resp = client.post(f'/variants/region/snv/{chrom}-{start}-{stop}',
                               json={'size': size, 'next': next},
                               follow_redirects=False)
        sv_resp = client.post(f'/variants/region/snv/{chrom}-{start}-{stop}',
                              json={'size': size, 'next': next},
                              follow_redirects=False)
    assert snv_resp.status_code == 303
    assert snv_resp.location == next
    assert sv_resp.status_code == 303
    assert sv_resp.location == next


def test_variants_post_alias(mocker):
    mock_sv = mocker.patch('bravo_api.api.get_region', side_effect=mock_json_response)
    mock_snv = mocker.patch('bravo_api.api.get_region_snv', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # post body content
    body = {'filters': [{'field': 'filter', 'type': '=', 'value': 'PASS'},
                        {'field': 'annotation.gene.consequence', 'type': '=',
                         'value': 'frameshift_variant'}],
            'introns': True}

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop,
                     'annotation.gene.consequence': 'eq:frameshift_variant', 'filter': 'eq:PASS'}

    with app.test_client() as client:
        client.post(f'/variants/region/snv/{chrom}-{start}-{stop}', json=body)
        client.post(f'/variants/region/sv/{chrom}-{start}-{stop}', json=body)
    mock_sv.assert_called_with(expected_args)
    mock_snv.assert_called_with(expected_args)


def test_variants_get_alias(mocker):
    mock_sv = mocker.patch('bravo_api.api.get_region', side_effect=mock_json_response)
    mock_snv = mocker.patch('bravo_api.api.get_region_snv', side_effect=mock_json_response)

    # path args
    chrom = '11'
    start = 500000
    stop = 5001000

    expected_args = {'chrom': chrom, 'start': start, 'stop': stop}

    with app.test_client() as client:
        client.get(f'/variants/region/snv/{chrom}-{start}-{stop}')
        client.get(f'/variants/region/sv/{chrom}-{start}-{stop}')
    mock_sv.assert_called_with(expected_args)
    mock_snv.assert_called_with(expected_args)


def test_gene_variants_redirect(mocker):
    # path args
    name = 'ENSG00000244734'
    size = 10000
    next = 'https://www.example.com/foo?bar=baz&duq=qux'

    with app.test_client() as client:
        resp = client.post(f'/variants/gene/snv/{name}',
                           json={'size': size, 'next': next}, follow_redirects=False)
    assert resp.status_code == 303
    assert resp.location == next


def test_gene_variants_post_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_gene_snv_impl', side_effect=mock_json_response)

    # path args
    name = 'ENSG00000244734'
    # post body content
    body = {"filters": [{"field": "filter", "type": "=", "value": "PASS"}],
            "introns": True,
            "size": 1000}

    expected_args = {'name': name, 'filter': 'eq:PASS', 'limit': 1000, 'introns': True}

    with app.test_client() as client:
        client.post(f'/variants/gene/snv/{name}', json=body)
    mock.assert_called_with(expected_args)


def test_gene_variants_get_alias(mocker):
    mock = mocker.patch('bravo_api.api.get_gene_snv_impl', side_effect=mock_json_response)

    # path args
    name = 'ENSG00000244734'

    expected_args = {'name': name}

    with app.test_client() as client:
        client.get(f'/variants/gene/snv/{name}')
    mock.assert_called_with(expected_args)
