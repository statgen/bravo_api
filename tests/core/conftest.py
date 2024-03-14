import pytest
import string
import random
import os
import boto3
import io
import gzip
from moto import mock_aws


# Mock coverage file structure
# coverage/
# ├── bin_0.25
# │   ├── chr1.bin_0.25.tsv.gz
# │   ├── chr1.bin_0.25.tsv.gz.tbi
# │   ├── chr2.bin_0.25.tsv.gz
# │   ├── chr2.bin_0.25.tsv.gz.tbi
# │   ├── ...
# │   ├── chrX.bin_0.25.tsv.gz
# │   └── chrX.bin_0.25.tsv.gz.tbi
# ├── bin_0.50
# │   └── ...
# ├── bin_0.75
# │   └── ...
# ├── bin_1.00
# │   └── ...
# └── full
#     ├── chr1.full.tsv.gz
#     ├── chr1.full.tsv.gz.tbi
#     ├── chr2.full.tsv.gz
#     ├── chr2.full.tsv.gz.tbi
#     ├── ...
#     ├── chr11.full.tsv.gz
#     ├── chr11.full.tsv.gz.tbi
#     ├── chrX.full.tsv.gz
#     └── chrX.full.tsv.gz.tbi


@pytest.fixture(scope="session")
def expected_bins():
    return(['bin_0.25', 'bin_0.50', 'bin_0.75', 'bin_1.00', 'full'])


@pytest.fixture(scope="session")
def incomplete_bins(expected_bins):
    return(expected_bins[1:])


@pytest.fixture(scope="session")
def expected_chroms():
    return(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
            '17', '18', '19', '20', '21', '22', 'X'])


@pytest.fixture(scope="session")
def sham_cov_dir(tmp_path_factory, expected_bins, expected_chroms):
    cov_dir = tmp_path_factory.mktemp('coverage')
    for cbin in expected_bins:
        cov_dir.joinpath(cbin).mkdir()

        for chrom in expected_chroms:
            cov_dir.joinpath(cbin, f'chr{chrom}.{cbin}.tsv.gz').touch()
            cov_dir.joinpath(cbin, f'chr{chrom}.{cbin}.tsv.gz.tbi').touch()

    return(str(cov_dir))


@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["MOTO_ALLOW_NONEXISTANT_REGION"] = 'True'
    os.environ["AWS_DEFAULT_REGION"] = "atlantis"


@pytest.fixture(scope="session")
def s3(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="atlantis")


@pytest.fixture(scope="session")
def sham_cov_url(s3, expected_bins, expected_chroms):
    """
    Create sham bucket with all bins and chroms stubbed out.
    Return url to of coverage prefix containing bins.
    """
    bucket_name = ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    prefix = 'coverage'
    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={'LocationConstraint': 'atlantis'})

    for cbin in expected_bins:
        for chrom in expected_chroms:
            s3.put_object(Bucket=bucket_name,
                          Key=f'{prefix}/{cbin}/chr{chrom}.{cbin}.tsv.gz',
                          Body='sham coverage content')
            s3.put_object(Bucket=bucket_name,
                          Key=f'{prefix}/{cbin}/chr{chrom}.{cbin}.tsv.gz.tbi',
                          Body='sham index content')

    return(f's3://{bucket_name}/{prefix}')


@pytest.fixture(scope="session")
def sham_incomplete_cov_url(s3, incomplete_bins, expected_chroms):
    """
    Create sham bucket missing an entire bin of chroms stubs.
    Return url to of coverage prefix containing bins.
    """
    bucket_name = ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    prefix = 'coverage'
    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={'LocationConstraint': 'atlantis'})

    for cbin in incomplete_bins:
        for chrom in expected_chroms:
            s3.put_object(Bucket=bucket_name,
                          Key=f'{prefix}/{cbin}/chr{chrom}.{cbin}.tsv.gz',
                          Body='sham coverage content')
            s3.put_object(Bucket=bucket_name,
                          Key=f'{prefix}/{cbin}/chr{chrom}.{cbin}.tsv.gz.tbi',
                          Body='sham index content')

    return(f's3://{bucket_name}/{prefix}')


# Mock crams file structure
# crams
# ├── variant_map.tsv.gz
# ├── variant_map.tsv.gz.tbi
# ├── sequences
# │   ├── 02
# │   │   ├── HGDP01075.cram
# │   │   └── HGDP01075.cram.crai
# │   ├── 11
# │   │   ├── HGDP00153.cram
# │   │   └── HGDP00153.cram.crai

@pytest.fixture(scope="session")
def mock_variant_map(mocker):
    mock_data = ["#RANDOM_SEED=8123", "#MAX_RANDOM_HOM_HETS=2", "#CHROM\tPOS\tREF\tALT\tHOM\tHET",
                 "chr11\t5220052\tG\tC\tHGDP00158,HGDP00645\tHGDP00557,HGDP00741",
                 "chr11\t5220161\tT\tA\t\tHGDP01077"]
    the_mock = mocker.mock_open(read_data=mock_data)
    return(the_mock)


@pytest.fixture(scope="session")
def sham_crams_dir(tmp_path_factory):
    crams_dir = tmp_path_factory.mktemp('crams')

    crams_dir.joinpath('variant_map.tsv.gz').touch()
    crams_dir.joinpath('variant_map.tsv.gz.tbi').touch()

    seq_dir = crams_dir.joinpath("sequences")
    seq_dir.mkdir()

    seq_dir.joinpath('02').mkdir()
    seq_dir.joinpath('02', 'HGDP01075.cram').touch()
    seq_dir.joinpath('02', 'HGDP01075.cram.crai').touch()

    seq_dir.joinpath('11').mkdir()
    seq_dir.joinpath('11', 'HGDP00153.cram').touch()
    seq_dir.joinpath('11', 'HGDP00153.cram.crai').touch()

    return(str(crams_dir))


@pytest.fixture(scope="session")
def sham_ref(tmp_path_factory):
    ref_dir = tmp_path_factory.mktemp('reference')
    ref_path = ref_dir.joinpath('hs38DH.fa')

    ref_path.touch()
    ref_dir.joinpath('hs38DH.fa.fai').touch()

    return(str(ref_path))


@pytest.fixture(scope="session")
def sham_varmap_gz():
    varmap = """#RANDOM_SEED=8123
             #MAX_RANDOM_HOM_HETS=3
             #SAMPLES_USED=50
             #CHROM\tPOS\tREF\tALT\tHOM\tHET
             chr11\t5220052\tG\tC\tHGDP00158,HGDP00645,HGDP00746\tHGDP00952,HGDP00557,HGDP00741
             chr11\t5220161\tT\tA\tHGDP01077
             chr11\t5220203\tT\tC\tHGDP00021
             """.encode('utf-8')
    b_out = io.BytesIO()
    with gzip.GzipFile(fileobj=b_out, mode="w") as out:
        out.write(varmap)
    return(b_out.read())


@pytest.fixture(scope="session")
def sham_crams_url(s3, sham_varmap_gz):
    """
    Create sham bucket with variant map and crams stubs.
    Return url to of coverage prefix containing bins.
    """
    bucket_name = ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    prefix = 'data/runtime/crams'
    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={'LocationConstraint': 'atlantis'})

    s3.put_object(Bucket=bucket_name, Key=f'{prefix}/variant_map.tsv.gz', Body=sham_varmap_gz)
    s3.put_object(Bucket=bucket_name, Key=f'{prefix}/variant_map.tsv.gz.tbi', Body="sham\tindex")

    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/sequences/00/ZZMH8C9KMY.cram', Body="sham\tcram")
    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/sequences/00/ZZMH8C9KMY.cram.crai', Body="sham\tcrai")
    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/sequences/ff/ANGIXJWFA6.cram', Body="sham\tcram")
    s3.put_object(Bucket=bucket_name,
                  Key=f'{prefix}/sequences/ff/ANGIXJWFA6.cram.crai', Body="sham\tcrai")

    return(f's3://{bucket_name}/{prefix}')
