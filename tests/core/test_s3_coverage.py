import pytest
from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
from bravo_api.core.s3_coverage_provider import S3CoverageProvider
from botocore.exceptions import ClientError


def test_smokes(sham_cov_url):
    cp = S3CoverageProvider(sham_cov_url)
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


def test_catalog_discovery_full(s3, sham_cov_url, expected_bins, expected_chroms):
    cp = S3CoverageProvider(sham_cov_url)

    # All bins are represented
    assert(set(cp.catalog.keys()) == set(expected_bins))

    # All chroms are represented in each bin
    for catalog_bin in cp.catalog.values():
        assert(set(catalog_bin.keys()) == set(expected_chroms))


def test_catalog_readability(sham_cov_url):
    cp = S3CoverageProvider(sham_cov_url)
    messages = cp.evaluate_chrom_readability()
    assert(len(messages) == 0)


def test_catalog_readability_denied(mocker, sham_cov_url):
    cp = S3CoverageProvider(sham_cov_url)

    mock_method = mocker.patch.object(cp.client, 'head_object')
    fake_err = ClientError({'Error': {'Code': '403', 'Message': 'Forbidden'}}, 'head_object')
    mock_method.side_effect = fake_err

    messages = cp.evaluate_chrom_readability()

    assert(len(messages) == mock_method.call_count)


def test_evaluate_chrom_representation(sham_cov_url):
    cp = S3CoverageProvider(sham_cov_url)
    messages = cp.evaluate_chrom_representation()
    assert(len(messages) == 0)


def test_evaluate_chrom_representation_incomplete(
    sham_incomplete_cov_url, incomplete_bins, expected_bins
):
    cp = S3CoverageProvider(sham_incomplete_cov_url)
    messages = cp.evaluate_chrom_representation()

    num_messages_expected = len(expected_bins) - len(incomplete_bins)
    assert(len(messages) == num_messages_expected)
