import pytest
from bravo_api.core.coverage_provider_factory import CoverageProviderFactory
from bravo_api.core.s3_coverage_provider import S3CoverageProvider
from bravo_api.core.fs_coverage_provider import FSCoverageProvider


def test_factory_makes_s3_coverage_provider(sham_cov_url):
    cp = CoverageProviderFactory.build(sham_cov_url)
    assert(isinstance(cp, S3CoverageProvider))


def test_factory_makes_fs_coverage_provider(sham_cov_dir):
    cp = CoverageProviderFactory.build(str(sham_cov_dir))
    assert(isinstance(cp, FSCoverageProvider))
