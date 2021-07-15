import pytest
from icecream import ic
from bravo_api.blueprints.legacy_ui import ui

SNV_QUERY = 'rs7'
SNV_DATA_KEYS = ['feature', 'variant_id',  'type']
SNV_RESULT = [{'allele_count': 47, 'allele_freq': 0.005632789805531502, 'allele_num': 8344,
               'annotation': {
                   'region': {
                       'consequence': ['intron_variant', 'NMD_transcript_variant',
                                       'non_coding_transcript_variant', 'upstream_gene_variant',
                                       'downstream_gene_variant']
                   }
               },
               'cadd_phred': 0.9879999756813049, 'chrom': '11', 'filter': [], 'het_count': 45,
               'hom_count': 1, 'pos': 5357967, 'rsids': ['rs7101402'], 'site_quality': 255.0,
               'stop': 5357967, 'variant_id': '11-5357967-G-T'
               },
              {'allele_count': 172, 'allele_freq': 0.020613599568605423, 'allele_num': 8344,
               'annotation': {
                   'region': {
                       'consequence': ['intron_variant', 'NMD_transcript_variant',
                                       'non_coding_transcript_variant']
                   }
               },
               'cadd_phred': 1.0149999856948853, 'chrom': '11', 'filter': [], 'het_count': 164,
               'hom_count': 4, 'pos': 5496433, 'rsids': ['rs7101611'], 'site_quality': 255.0,
               'stop': 5496433, 'variant_id': '11-5496433-T-C'
               },
              {'allele_count': 217, 'allele_freq': 0.026006700471043587, 'allele_num': 8344,
               'annotation': {
                   'region': {
                       'consequence': ['intron_variant', 'NMD_transcript_variant',
                                       'non_coding_transcript_variant', 'upstream_gene_variant']
                   }
               },
               'cadd_phred': 1.649999976158142, 'chrom': '11', 'filter': [], 'het_count': 195,
               'hom_count': 11, 'pos': 5401744, 'rsids': ['rs7101836'], 'site_quality': 255.0,
               'stop': 5401744, 'variant_id': '11-5401744-A-C'
               }
              ]


# Mock of variants.get_snv
def empty_snv(name, full):
    return
    yield


# Mock of variants.get_snv
def rs_snv_results(name, chrom, positon, full):
    yield from SNV_RESULT


def test_empty_result(monkeypatch):
    monkeypatch.setattr(ui.variants, 'get_snv', empty_snv)
    result = ui.search_variant_ids('')
    assert type(result) is list
    assert len(result) == 0


def test_result_length(monkeypatch):
    monkeypatch.setattr(ui.variants, 'get_snv', rs_snv_results)
    result = ui.search_variant_ids(SNV_QUERY)
    assert type(result) is list
    assert len(list(result)) == 3


def test_result_keys(monkeypatch):
    monkeypatch.setattr(ui.variants, 'get_snv', rs_snv_results)
    result = ui.search_variant_ids(SNV_QUERY)
    for item in result:
        data = item['data']
        ic(data.keys())
        assert type(data) is dict
        assert len(data.keys()) == len(SNV_DATA_KEYS)
        assert all(key in SNV_DATA_KEYS for key in data.keys())
