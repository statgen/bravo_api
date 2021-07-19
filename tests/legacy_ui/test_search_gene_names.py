import pytest
from icecream import ic
from bravo_api.blueprints.legacy_ui import autocomplete

GENE_QUERY = 'HBB'
GENE_RESULT = [{'chrom': '11', 'full_gene_name': 'hemoglobin subunit beta pseudogene 1',
                'gene_id': 'ENSG00000229988', 'gene_name': 'HBBP1',
                'gene_type': 'transcribed_unprocessed_pseudogene', 'other_names': ['HBH1, HBHP'],
                'start': 5241105, 'stop': 5243537, 'strand': '-'},
               {'chrom': '11', 'full_gene_name': 'hemoglobin subunit beta',
                'gene_id': 'ENSG00000244734', 'gene_name': 'HBB', 'gene_type': 'protein_coding',
                'omim_accession': '141900', 'omim_description': 'HEMOGLOBIN--BETA LOCUS; HBB',
                'other_names': ['CD113t-C, beta-globin'], 'start': 5225464, 'stop': 5229395,
                'strand': '-'}]

RESULT_DATA_KEYS = ['feature', 'chrom',  'start',  'stop',   'type']


# Mock of variants.get_genes
def empty_gene_names(name, full):
    return
    yield


def hbb_gene_name_results(name, full):
    yield from GENE_RESULT


def test_empty_result(monkeypatch):
    monkeypatch.setattr(autocomplete.variants, 'get_genes', empty_gene_names)
    result = autocomplete.search_gene_names('')
    assert type(result) is list


def test_result_length(monkeypatch):
    monkeypatch.setattr(autocomplete.variants, 'get_genes', hbb_gene_name_results)
    result = autocomplete.search_gene_names(GENE_QUERY)
    assert type(result) is list
    assert len(list(result)) == 2


def test_result_keys(monkeypatch):
    monkeypatch.setattr(autocomplete.variants, 'get_genes', hbb_gene_name_results)
    result = autocomplete.search_gene_names(GENE_QUERY)
    for item in result:
        data = item['data']
        ic(data.keys())
        assert type(data) is dict
        assert len(data.keys()) == len(RESULT_DATA_KEYS)
        assert all(key in RESULT_DATA_KEYS for key in data.keys())


@pytest.mark.skip(reason="Work in progress")
def test_search_variant_ids_empty_query():
    result = autocomplete.search_variant_ids('')
    assert type(result) is list
    pass


@pytest.mark.skip(reason="Work in progress")
def test_search_autocomplete():
    pass
