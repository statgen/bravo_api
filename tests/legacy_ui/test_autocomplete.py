from bravo_api.blueprints.legacy_ui import autocomplete

# Mock empty snv or gene results
def empty_query_result(name, full):
    return
    yield

def test_empty_gene_and_snv_results(monkeypatch):
    monkeypatch.setattr(autocomplete.variants, 'get_snv', empty_query_result)
    monkeypatch.setattr(autocomplete.variants, 'get_gene', empty_query_result)

    result = autocomplete.search_variant_ids('')
    assert type(result) is list
    assert len(result) == 0
