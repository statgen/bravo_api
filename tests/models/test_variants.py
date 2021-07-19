from bravo_api.models import variants


def test_get_snv(patch_variants_mongo):
    result = variants.get_snv('', None, None, False)
    assert len(list(result)) == 0


def test_get_genes_empty_query(patch_variants_mongo):
    result = variants.get_genes('', False)
    assert len(list(result)) == 0


def test_get_genes_filter_includes_limit(patch_variants_mongo):
    result = variants.get_genes('', False)
    assert len(list(result)) == 0


def test_basic_genes_pipeline_for_gene_names():
    result = variants.basic_genes_pipeline('foo')

    assert type(result) is list
    assert len(result) == 4
    assert 'gene_name' in result[0]['$match'].keys()
    assert result[-1] == {'$limit': 10}


def test_basic_genes_pipeline_for_gene_ids():
    result = variants.basic_genes_pipeline('ENSG00000000001')

    assert type(result) is list
    assert len(result) == 4
    assert 'gene_id' in result[0]['$match'].keys()
    assert result[-1] == {'$limit': 10}