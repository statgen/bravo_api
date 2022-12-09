import pytest
from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
from bravo_api.core.fs_coverage_provider import FSCoverageProvider


def test_smokes(sham_cov_dir):
    cp = FSCoverageProvider(sham_cov_dir)
    assert isinstance(cp, CoverageProvider)


def test_catalog_discovery(sham_cov_dir, expected_bins, expected_chroms):
    cp = FSCoverageProvider(sham_cov_dir)

    # All bins are represented
    assert(set(cp.catalog.keys()) == set(expected_bins))

    # All chroms are represented in each bin
    for catalog_bin in cp.catalog.values():
        assert(set(catalog_bin.keys()) == set(expected_chroms))


def test_missing_source_error():
    with pytest.raises(CoverageSourceInaccessibleError):
        FSCoverageProvider('does/not/exist')


def test_non_dir_source_error(tmp_path_factory):
    a_dir = tmp_path_factory.mktemp('foo')
    a_file_path = a_dir.joinpath('bar')
    a_file_path.touch()

    with pytest.raises(CoverageSourceInaccessibleError):
        FSCoverageProvider(a_file_path)


def test_no_access_source_error(tmp_path_factory):
    a_dir = tmp_path_factory.mktemp('foo')
    a_file_path = a_dir.joinpath('bar')
    a_file_path.touch()

    with pytest.raises(CoverageSourceInaccessibleError):
        FSCoverageProvider(a_file_path)


def test_evaluate_chrom_representation_full(sham_cov_dir):
    """
    Full coverage directory should have no warning messages
    """
    cp = FSCoverageProvider(sham_cov_dir)
    warnings = cp.evaluate_chrom_representation()

    assert(len(warnings) == 0)


def test_evaluate_chrom_representation_empty(tmp_path_factory, expected_bins):
    """
    Empty coverage should warn missing chroms for every bin
    """
    a_dir = tmp_path_factory.mktemp('bar')
    cp = FSCoverageProvider(a_dir)

    warnings = cp.evaluate_chrom_representation()
    assert(len(warnings) == len(expected_bins))


def test_evaluate_chrom_readability_full(sham_cov_dir):
    """
    Full coverage directory should have no readability warning messages
    """
    cp = FSCoverageProvider(sham_cov_dir)
    warnings = cp.evaluate_chrom_readability()

    assert(len(warnings) == 0)


def test_evaluate_chrom_readability_unreadable(tmp_path_factory, expected_bins, expected_chroms):
    """
    Should generate one message per unreadable coverage file.
    """
    cov_dir = tmp_path_factory.mktemp('baz')
    number_unreadable = 0
    for cbin in expected_bins:
        cov_dir.joinpath(cbin).mkdir()
        for chrom in expected_chroms:
            cov_dir.joinpath(cbin, f'chr{chrom}.{cbin}.tsv.gz').touch(mode=0o333)
            cov_dir.joinpath(cbin, f'chr{chrom}.{cbin}.tsv.gz.tbi').touch(mode=0o333)
            number_unreadable += 2

    cp = FSCoverageProvider(cov_dir)
    warnings = cp.evaluate_chrom_readability()

    assert(len(warnings) == number_unreadable)
