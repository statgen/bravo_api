import pytest
import random
import io
from pathlib import Path
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError, VariantMapError)
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

sham_varmap_path = Path('/sham/crams/variant_map.tsv.gz')

varmap_header = """#RANDOM_SEED=8123
#MAX_RANDOM_HOM_HETS=5
#SAMPLES_USED=50
#CHROM  POS     REF     ALT     HOM     HET
"""

varmap_header_missing = """#RANDOM_SEED=8123
#SAMPLES_USED=50
#CHROM  POS     REF     ALT     HOM     HET
"""

varmap_header_bad = """#RANDOM_SEED=8123
#MAX_RANDOM_HOM_HETS=-1
#SAMPLES_USED=50
#CHROM  POS     REF     ALT     HOM     HET
"""


def test_extract_max_het_hom(mocker):
    m = mocker.mock_open(read_data=varmap_header)
    mocker.patch('gzip.open', m)

    result = FSCramSource.extract_max_het_hom(sham_varmap_path)
    assert(result == 5)


def test_missing_max_het_hom(mocker):
    m = mocker.mock_open(read_data=varmap_header_missing)
    mocker.patch('gzip.open', m)

    with pytest.raises(VariantMapError, match='missing'):
        FSCramSource.extract_max_het_hom(sham_varmap_path)


def test_bad_max_het_hom(mocker):
    m = mocker.mock_open(read_data=varmap_header_bad)
    mocker.patch('gzip.open', m)

    with pytest.raises(VariantMapError, match='invalid'):
        FSCramSource.extract_max_het_hom(sham_varmap_path)


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
