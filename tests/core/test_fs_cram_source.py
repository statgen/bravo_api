import pytest
import random
import io
from pathlib import Path
from pysam import TabixFile
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError)
from bravo_api.core.fs_cram_source import FSCramSource


# Need python class to avoid error trying to mock TabixFile.__enter__
#   Can't set attributes of built-in/extension type 'pysam.libctabix.TabixFile'
class FakeTabix:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def fetch(self, *args):
        return self.rows


itabix_contigs = ['chr1', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17',
                  'chr18', 'chr19', 'chr2', 'chr20', 'chr21', 'chr22', 'chr3', 'chr4', 'chr5',
                  'chr6', 'chr7', 'chr8', 'chr9', 'chrX']

expected_contigs = {'chr1', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17',
                    'chr18', 'chr19', 'chr2', 'chr20', 'chr21', 'chr22', 'chr3', 'chr4', 'chr5',
                    'chr6', 'chr7', 'chr8', 'chr9', 'chrX'}

sham_bam_subset = {'bam': random.randbytes(20000), 'bai': random.randbytes(1000)}

sham_varmap_path = Path('/no/such/file.tsv.gz')


def test_init(mocker, sham_crams_dir, sham_ref):
    # Mock out interface that reads from the variant map
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_max_het_hom', return_value=5)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_contigs',
                 return_value=expected_contigs)

    cs = FSCramSource(sham_crams_dir, sham_ref)
    assert(isinstance(cs, CramSource))


def test_structural_validation(mocker, tmp_path_factory):
    # Mock out interface that reads from the variant map
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_max_het_hom', return_value=5)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_contigs',
                 return_value=expected_contigs)

    with pytest.raises(CramSourceInaccessibleError, match='extant directory'):
        FSCramSource('crams/dir/not/exist', 'ref/path/not/exist.fa')
    crams_dir = tmp_path_factory.mktemp('crams')

    with pytest.raises(CramSourceInaccessibleError, match='contain "sequences"'):
        FSCramSource(crams_dir, 'ref/path/not/exist.fa')
    seq_dir = crams_dir.joinpath("sequences")
    seq_dir.mkdir()

    with pytest.raises(CramSourceInaccessibleError, match='contain variant_map'):
        FSCramSource(crams_dir, 'ref/path/not/exist.fa')
    crams_dir.joinpath('variant_map.tsv.gz').touch()

    with pytest.raises(CramSourceInaccessibleError, match='contain variant_map index'):
        FSCramSource(crams_dir, 'ref/path/not/exist.fa')
    crams_dir.joinpath('variant_map.tsv.gz.tbi').touch()

    with pytest.raises(ReferenceInaccessibleError, match='Reference file'):
        FSCramSource(crams_dir, 'ref/path/not/exist.fa')
    ref_dir = tmp_path_factory.mktemp('reference')
    ref_path = ref_dir.joinpath('hs38DH.fa')
    ref_path.touch()

    with pytest.raises(ReferenceInaccessibleError, match='Reference file index'):
        FSCramSource(crams_dir, ref_path)
    ref_dir.joinpath('hs38DH.fa.fai').touch()

    assert(FSCramSource(crams_dir, ref_path).validate() is True)


def test_present_contig_prefix_detection():
    result = FSCramSource.are_contigs_chr_prefixed(expected_contigs)
    assert(result is True)


def test_absent_contig_prefix_detection():
    unprefixed_contigs = {'1', '2', '3', '4', 'X'}
    result = FSCramSource.are_contigs_chr_prefixed(unprefixed_contigs)
    assert(result is False)


def test_contig_naming_normalization_flipping():
    contigs_chr_prefixed = False
    result = FSCramSource.normalize_contig_prefix('chr20', contigs_chr_prefixed)
    assert(result == '20')

    contigs_chr_prefixed = True
    result = FSCramSource.normalize_contig_prefix('20', contigs_chr_prefixed)
    assert(result == 'chr20')


def test_contig_naming_normalization_unchanging():
    input_contig = 'chr10'
    contigs_chr_prefixed = True
    result = FSCramSource.normalize_contig_prefix(input_contig, contigs_chr_prefixed)
    assert(result == input_contig)

    input_contig = '10'
    contigs_chr_prefixed = False
    result = FSCramSource.normalize_contig_prefix(input_contig, contigs_chr_prefixed)
    assert(result == input_contig)


def test_get_sequences_info(mocker):
    # Mock TabixFile.fetch
    info = [("chr11", "5225059", "G", "A", "TYDMWW55F3,QQKVV21VJJ",
             "DL4E60CPZB,6BGL5F8760,L3SSV0VZ3K,5E6WOA9HZ3,HKHEDNSJC5")]
    attrs = {'fetch.return_value': info}
    tabix_mock = mocker.Mock(TabixFile, **attrs)

    expected = [{'n_homozygous': 2, 'n_heterozygous': 5}]
    result = FSCramSource.het_hom_counts(tabix_mock, 'chr11', 5225059, 'G', 'A')

    assert(result == expected)


def test_no_homs_get_sequences_info(mocker):
    # Mock TabixFile.fetch
    no_homs = [("chr11", "5225001", "C", "T", "",  "TPWASH61GW,DPJAT56WLO,1FX5WVQX36,DHQVG4X5FP")]
    attrs = {'fetch.return_value': no_homs}
    tabix_mock = mocker.Mock(TabixFile, **attrs)

    expected = [{'n_homozygous': 0, 'n_heterozygous': 4}]
    result = FSCramSource.het_hom_counts(tabix_mock, 'chr11', 5225001, 'C', 'T')

    assert(result == expected)


def test_stop_byte_correction():
    result = FSCramSource.rectify_stop_byte(start=0, stop=100, data_size=1000)
    assert(result == 101)


def test_stop_byte_missing():
    data_size = 1000
    result = FSCramSource.rectify_stop_byte(start=0, stop=None, data_size=data_size)
    assert(result == data_size)


def test_stop_byte_zero():
    result = FSCramSource.rectify_stop_byte(start=0, stop=0, data_size=1000)
    assert(result == 1)


def test_stop_byte_negative():
    data_size = 1000
    result = FSCramSource.rectify_stop_byte(start=0, stop=-10, data_size=data_size)
    assert(result == data_size)


def test_extract_hom_sample_id():
    row = 'chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'
    result = FSCramSource.extract_sample_id(row, 5220052, 'G', 'C', None, 1)
    assert(result == 'HGDP00158')


def test_extract_het_sample_id():
    row = 'chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'
    result = FSCramSource.extract_sample_id(row, 5220052, 'G', 'C', True, 2)
    assert(result == 'HGDP00741')


def test_extract_sample_id_no_match():
    row = 'chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'
    result = FSCramSource.extract_sample_id(row, 5220052, 'T', 'C', None, 1)
    assert(result is None)


def test_lookup_sample_id(mocker):
    mock_rows = [('chr11', '5220052', 'G', 'C', 'HGDP00158,HGDP00645', 'HGDP00557,HGDP00741'),
                 ('chr11', '5220052', 'G', 'TA', 'HGDP00999,HGDP00888', 'HGDP00777,HGDP00666')]

    mocker.patch('bravo_api.core.fs_cram_source.pysam.TabixFile',
                 return_value=FakeTabix(mock_rows))

    result = FSCramSource.lookup_sample_id(sham_varmap_path, 'chr11', '5220052', 'G', 'C', True, 2)
    assert(result == 'HGDP00741')


def test_get_cram_1k_bytes(mocker, sham_crams_dir, sham_ref):
    # Mock out interfaces that reads from disk
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_max_het_hom', return_value=5)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_contigs',
                 return_value=expected_contigs)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.lookup_sample_id',
                 return_value='SHAMID')
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_bam_subset',
                 return_value=sham_bam_subset)

    cs = FSCramSource(sham_crams_dir, sham_ref)
    result = cs.get_cram('chr11-500000-A-C', 1, False, 0, 999)

    assert(isinstance(result['file_bytes'], io.BytesIO))
    assert len(result['file_bytes'].read()) == 1000


def test_get_cram_all_bytes(mocker, sham_crams_dir, sham_ref):
    # Mock out interfaces that reads from disk
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_max_het_hom', return_value=5)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_contigs',
                 return_value=expected_contigs)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.lookup_sample_id',
                 return_value='SHAMID')
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_bam_subset',
                 return_value=sham_bam_subset)

    cs = FSCramSource(sham_crams_dir, sham_ref)
    result = cs.get_cram('chr11-500000-A-C', 1, False, 0, None)

    assert(isinstance(result['file_bytes'], io.BytesIO))
    assert result['file_bytes'].read() == sham_bam_subset['bam']


def test_get_crai(mocker, sham_crams_dir, sham_ref):
    # Mock out interfaces that reads from disk
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_max_het_hom', return_value=5)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_contigs',
                 return_value=expected_contigs)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.lookup_sample_id',
                 return_value='SHAMID')
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_bam_subset',
                 return_value=sham_bam_subset)

    cs = FSCramSource(sham_crams_dir, sham_ref)
    result = cs.get_crai('chr11-500000-A-C', 1, False)

    assert(isinstance(result, io.BytesIO))
    assert result.read() == sham_bam_subset['bai']


def test_cram_path(mocker, sham_crams_dir, sham_ref):
    # Mock out interface that reads from the variant map
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_max_het_hom', return_value=5)
    mocker.patch('bravo_api.core.fs_cram_source.FSCramSource.extract_contigs',
                 return_value=expected_contigs)

    cs = FSCramSource(sham_crams_dir, sham_ref)
    result = cs.calc_cram_path('HGDP01075')
    expected = f'{sham_crams_dir}/sequences/02/HGDP01075.cram'
    assert(result == expected)
