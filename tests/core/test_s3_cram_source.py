import pytest
import random
import string
from pathlib import Path
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError)
from bravo_api.core.s3_cram_source import S3CramSource


class FakeTabix:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def fetch(self, *args):
        return self.rows


expected_contigs = {'chr1', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17',
                    'chr18', 'chr19', 'chr2', 'chr20', 'chr21', 'chr22', 'chr3', 'chr4', 'chr5',
                    'chr6', 'chr7', 'chr8', 'chr9', 'chrX'}


def test_init(mocker, sham_crams_url, sham_ref):
    # Mock out interface that reads from the variant map
    mocker.patch('bravo_api.core.s3_cram_source.S3CramSource.extract_max_het_hom', return_value=3)
    mocker.patch('bravo_api.core.s3_cram_source.S3CramSource.extract_contigs',
                 return_value=expected_contigs)

    cs = S3CramSource(sham_crams_url, sham_ref)
    assert(isinstance(cs, CramSource))


def test_ref_file_validation(sham_ref):
    result = S3CramSource.validate_ref_path(Path(sham_ref))
    assert(result is True)


def test_ref_file_missing_validation(tmp_path_factory):
    bad_path = Path('ref/path/not/exist.fa')
    with pytest.raises(ReferenceInaccessibleError, match='Reference file'):
        S3CramSource.validate_ref_path(bad_path)

    ref_dir = tmp_path_factory.mktemp('reference')
    ref_path = ref_dir.joinpath('hs38DH.fa')
    ref_path.touch()

    with pytest.raises(ReferenceInaccessibleError, match='Reference file index'):
        S3CramSource.validate_ref_path(ref_path)
    ref_dir.joinpath('hs38DH.fa.fai').touch()

    result = S3CramSource.validate_ref_path(ref_path)
    assert(result is True)


def test_bucket_validation(s3, sham_crams_url):
    result = S3CramSource.validate_bucket_varmap(sham_crams_url, s3)
    assert(result is True)


def test_bucket_validation_badurl(s3, sham_crams_url):
    bad_url = '/actually/path/on/disk/crams'

    with pytest.raises(CramSourceInaccessibleError, match=r"Url scheme is not s3"):
        S3CramSource.validate_bucket_varmap(bad_url, s3)


def test_bucket_validation_varmap_missing(s3):
    bucket_name = ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    prefix = 'crams'
    url = f's3://{bucket_name}/{prefix}'

    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={'LocationConstraint': 'atlantis'})

    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/readme.md', Body="sham readme")

    with pytest.raises(CramSourceInaccessibleError, match=r"Missing variant map"):
        S3CramSource.validate_bucket_varmap(url, s3)

    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/variant_map.tsv.gz', Body="sham\tvar\tmap")

    with pytest.raises(CramSourceInaccessibleError, match=r"Missing variant map index"):
        S3CramSource.validate_bucket_varmap(url, s3)

    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/variant_map.tsv.gz.tbi', Body="sham\tvar\tmap")

    result = S3CramSource.validate_bucket_varmap(url, s3)
    assert(result is True)


def test_bucket_validation_cram_files_present(s3, sham_crams_url):
    result = S3CramSource.validate_bucket_crams(sham_crams_url, s3)
    assert(result is True)


def test_bucket_validation_cram_files_missing(s3):
    bucket_name = ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    prefix = 'crams'
    url = f's3://{bucket_name}/{prefix}'

    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={'LocationConstraint': 'atlantis'})

    with pytest.raises(CramSourceInaccessibleError, match=r"is empty"):
        S3CramSource.validate_bucket_crams(url, s3)

    s3.put_object(Bucket=bucket_name, Key=f'{prefix}/sequences/00/not_a_cram', Body="bad data")
    s3.put_object(Bucket=bucket_name, Key=f'{prefix}/sequences/ff/not_a_cram', Body="bad data")

    with pytest.raises(CramSourceInaccessibleError, match=r"No cram files found"):
        S3CramSource.validate_bucket_crams(url, s3)
