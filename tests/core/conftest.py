import pytest
import string
import random
import os
import boto3
from moto import mock_s3

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

    return(cov_dir)


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
    with mock_s3():
        yield boto3.client("s3", region_name="atlantis")


@pytest.fixture(scope="session")
def sham_cov_bucket(s3, expected_bins, expected_chroms):
    bucket_name = 'test-'.join([random.choice(string.ascii_lowercase) for i in range(8)])
    s3.create_bucket(Bucket=bucket_name,
                     CreateBucketConfiguration={'LocationConstraint': 'atlantis'})

    for cbin in expected_bins:
        for chrom in expected_chroms:
            s3.put_object(Bucket=bucket_name,
                          Key=f'coverage/{cbin}/chr{chrom}.{cbin}.tsv.gz',
                          Body='sham coverage content')
            s3.put_object(Bucket=bucket_name,
                          Key=f'coverage/{cbin}/chr{chrom}.{cbin}.tsv.gz.tbi',
                          Body='sham index content')

    return(bucket_name)
