import pytest
import pdb
from unittest import TestCase
from bravo_api.models import variants


def test_build_mongo_filter():
    user_filter = {'annotation': {'gene': {'consequence': [
        {'$eq': ['start_retained_variant']},
        {'$eq': ['stop_retained_variant']},
        {'$eq': ['synonymous_variant']}
    ]}}}

    expected_result = [{"$or": [
        {"$and": [{"annotation.genes.consequence": {"$eq": "start_retained_variant"}}]},
        {"$and": [{"annotation.genes.consequence": {"$eq": "stop_retained_variant"}}]},
        {"$and": [{"annotation.genes.consequence": {"$eq": "synonymous_variant"}}]}
    ]}]

    result = variants.build_mongo_filter(user_filter)
    assert expected_result == result


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


def test_full_genes_pipeline_appended():
    result = variants.full_genes_pipeline('ENSG00000000001')
    expected_tail = variants.GET_GENES_FULL_LOOKUP_ADDON
    # The list constant should be appended.
    assert isinstance(result, list)
    assert result[-len(expected_tail):] == expected_tail
