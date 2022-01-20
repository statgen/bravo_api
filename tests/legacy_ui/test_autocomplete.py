from unittest.mock import patch
from bravo_api.blueprints.legacy_ui import autocomplete


# Mock empty snv or gene results
def empty_query_result(name, full):
    return
    yield


def test_empty_variant_results(monkeypatch):
    monkeypatch.setattr(autocomplete.variants, 'get_snv', empty_query_result)

    result = autocomplete.search_variant_ids('example')

    assert type(result) is list
    assert len(result) == 0


def test_empty_gene_results(monkeypatch):
    monkeypatch.setattr(autocomplete.variants, 'get_genes', empty_query_result)

    result = autocomplete.search_gene_names('example')

    assert type(result) is list
    assert len(result) == 0


# Aggregation suggestions are combination of gene and variant results.
@patch('bravo_api.blueprints.legacy_ui.autocomplete.search_variant_ids')
@patch('bravo_api.blueprints.legacy_ui.autocomplete.search_gene_names')
def test_aggregate_combined_results(search_gene_patch, search_variant_patch):
    mock_genes = [{'x': 33}]
    mock_variants = [{'x': val} for val in range(100, 110)]

    search_gene_patch.return_value = mock_genes
    search_variant_patch.return_value = mock_variants

    result = autocomplete.aggregate('rs1')
    suggestions = result['suggestions']

    mock_genes_in_suggestions = [it in suggestions for it in mock_genes]
    mock_variants_in_suggestions = [it in suggestions for it in mock_variants]

    assert(len(suggestions) == (len(mock_genes) + len(mock_variants)))
    assert(all(mock_genes_in_suggestions))
    assert(all(mock_variants_in_suggestions))


# Aggregation only calls gene query when 10 or more results.
@patch('bravo_api.blueprints.legacy_ui.autocomplete.search_variant_ids')
@patch('bravo_api.blueprints.legacy_ui.autocomplete.search_gene_names')
def test_autocomplete_preclude(search_gene_patch, search_variant_patch):
    mock_genes = [{'x': val} for val in range(0, 10)]
    mock_variants = [{'x': val} for val in range(100, 110)]

    search_gene_patch.return_value = mock_genes
    search_variant_patch.return_value = mock_variants

    autocomplete.aggregate('example')

    assert(len(search_gene_patch.mock_calls) == 1)
    assert(len(search_variant_patch.mock_calls) == 0)


# Aggregation calls gene + variant query when fewer than 10 gene results.
@patch('bravo_api.blueprints.legacy_ui.autocomplete.search_variant_ids')
@patch('bravo_api.blueprints.legacy_ui.autocomplete.search_gene_names')
def test_autocomplete_combination(search_gene_patch, search_variant_patch):
    search_gene_patch.return_value = [{} for x in range(5)]
    search_variant_patch.return_value = [{} for x in range(11)]

    autocomplete.aggregate('example')

    assert(len(search_gene_patch.mock_calls) == 1)
    assert(len(search_variant_patch.mock_calls) == 1)


@patch('bravo_api.blueprints.legacy_ui.autocomplete.aggregate')
def test_autocomplete(aggregate_patch, client):
    aggregate_patch.return_value = {'suggestions': [{}, {}, {}]}
    resp = client.get('/autocomplete?query=example')
    assert(resp.status_code == 200)
    assert(resp.content_type == 'application/json')
