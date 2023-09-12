import pytest
from pysam import TabixFile
from bravo_api.core.cram_source import CramSource


def test_get_sequences_info(mocker):
    # Mock TabixFile.fetch
    info = [("chr11", "5225059", "G", "A", "TYDMWW55F3,QQKVV21VJJ",
             "DL4E60CPZB,6BGL5F8760,L3SSV0VZ3K,5E6WOA9HZ3,HKHEDNSJC5")]
    attrs = {'fetch.return_value': info}
    tabix_mock = mocker.Mock(TabixFile, **attrs)

    expected = [{'n_homozygous': 2, 'n_heterozygous': 5}]
    result = CramSource.het_hom_counts(tabix_mock, 'chr11', 5225059, 'G', 'A')

    assert(result == expected)


def test_no_homs_get_sequences_info(mocker):
    # Mock TabixFile.fetch
    no_homs = [("chr11", "5225001", "C", "T", "",  "TPWASH61GW,DPJAT56WLO,1FX5WVQX36,DHQVG4X5FP")]
    attrs = {'fetch.return_value': no_homs}
    tabix_mock = mocker.Mock(TabixFile, **attrs)

    expected = [{'n_homozygous': 0, 'n_heterozygous': 4}]
    result = CramSource.het_hom_counts(tabix_mock, 'chr11', 5225001, 'C', 'T')

    assert(result == expected)


def test_contig_naming_normalization_unchanging():
    input_contig = 'chr10'
    contigs_chr_prefixed = True
    result = CramSource.normalize_contig_prefix(input_contig, contigs_chr_prefixed)
    assert(result == input_contig)

    input_contig = '10'
    contigs_chr_prefixed = False
    result = CramSource.normalize_contig_prefix(input_contig, contigs_chr_prefixed)
    assert(result == input_contig)


def test_present_contig_prefix_detection():
    prefixed_contigs = {'chr1', 'chr2', 'chr3', 'chr4', 'chrX'}
    result = CramSource.are_contigs_chr_prefixed(prefixed_contigs)
    assert(result is True)


def test_absent_contig_prefix_detection():
    unprefixed_contigs = {'1', '2', '3', '4', 'X'}
    result = CramSource.are_contigs_chr_prefixed(unprefixed_contigs)
    assert(result is False)


def test_contig_naming_normalization_flipping():
    contigs_chr_prefixed = False
    result = CramSource.normalize_contig_prefix('chr20', contigs_chr_prefixed)
    assert(result == '20')

    contigs_chr_prefixed = True
    result = CramSource.normalize_contig_prefix('20', contigs_chr_prefixed)
    assert(result == 'chr20')


def test_stop_byte_correction():
    result = CramSource.rectify_stop_byte(start=0, stop=100, data_size=1000)
    assert(result == 101)


def test_stop_byte_missing():
    data_size = 1000
    result = CramSource.rectify_stop_byte(start=0, stop=None, data_size=data_size)
    assert(result == data_size)


def test_stop_byte_zero():
    result = CramSource.rectify_stop_byte(start=0, stop=0, data_size=1000)
    assert(result == 1)


def test_stop_byte_negative():
    data_size = 1000
    result = CramSource.rectify_stop_byte(start=0, stop=-10, data_size=data_size)
    assert(result == data_size)


def test_extract_hom_sample_id():
    row = 'chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'
    result = CramSource.extract_sample_id(row, 5220052, 'G', 'C', None, 1)
    assert(result == 'HGDP00158')


def test_extract_het_sample_id():
    row = 'chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'
    result = CramSource.extract_sample_id(row, 5220052, 'G', 'C', True, 2)
    assert(result == 'HGDP00741')


def test_extract_sample_id_no_match():
    row = 'chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'
    result = CramSource.extract_sample_id(row, 5220052, 'T', 'C', None, 1)
    assert(result is None)
