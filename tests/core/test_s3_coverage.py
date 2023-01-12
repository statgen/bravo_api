import pytest
from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
from bravo_api.core.s3_coverage_provider import S3CoverageProvider
from botocore.exceptions import ClientError


def test_smokes(sham_cov_bucket):
    cp = S3CoverageProvider(f's3://{sham_cov_bucket}')
    assert(isinstance(cp, CoverageProvider))


def test_missing_source_error(mocker):
    # Set up mocks
    fake_msg = 'Testing bucket does not exist.'
    fake_code = 'NoSuchBucket'
    fake_err = ClientError({'Error': {'Code': fake_code, 'Message': fake_msg}}, 'list_objects_v2')
    attrs = {'list_objects_v2.side_effect': fake_err}
    inst_mock = mocker.MagicMock()
    inst_mock.configure_mock(**attrs)
    class_mock = mocker.patch('bravo_api.core.s3_coverage_provider.boto3.client',
                              return_value=inst_mock)

    # Do call
    with pytest.raises(CoverageSourceInaccessibleError) as err:
        S3CoverageProvider('s3://non-existant-bucket/coverage-prefix')

    # Verify expected calls
    class_mock.assert_called_once_with('s3')
    inst_mock.list_objects_v2.assert_called_once_with(Bucket='non-existant-bucket',
                                                      Prefix='coverage-prefix',
                                                      MaxKeys=10)
    # Verify informative error thrown
    assert(err.match(fake_msg))
