import pytest
from pysam import TabixFile
from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
from bravo_api.core.fs_coverage_provider import FSCoverageProvider


def test_smokes(sham_cov_dir):
    cp = FSCoverageProvider(sham_cov_dir)
    assert(isinstance(cp, CoverageProvider))


def test_catalog_discovery(sham_cov_dir, expected_bins, expected_chroms):
    cp = FSCoverageProvider(sham_cov_dir)
    all_paths = [pth
                 for cov_bin in cp.catalog.values()
                 for pth in cov_bin.values()]

    # All bins are represented
    assert(set(cp.catalog.keys()) == set(expected_bins))

    # All chroms are represented in each bin
    for catalog_bin in cp.catalog.values():
        assert(set(catalog_bin.keys()) == set(expected_chroms))

    # Catalog is not using the index .tbi or .csi files.
    for path in all_paths:
        assert(path.suffix == '.gz')


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


def test_evaluate_catalog_consolidates_warnings(mocker, sham_cov_dir):
    # Patch underlying evaluations
    repesentation_warns = ['foo', 'bar']
    readability_warns = ['baz', 'duq']

    module_name = 'bravo_api.core.fs_coverage_provider.FSCoverageProvider'
    mocker.patch(f'{module_name}.evaluate_chrom_representation', return_value=repesentation_warns)
    mocker.patch(f'{module_name}.evaluate_chrom_readability', return_value=readability_warns)

    # Verify top level evaluation returns aggregate of underlying eval results
    cp = FSCoverageProvider(sham_cov_dir)
    assert(set(cp.evaluate_catalog()) == set().union(repesentation_warns, readability_warns))


def test_good_coverage_file_lookup(sham_cov_dir, expected_bins, expected_chroms):
    cp = FSCoverageProvider(sham_cov_dir)
    for cbin in expected_bins:
        for chrom in expected_chroms:
            assert(cp.lookup_coverage_path(cbin, chrom) is not None)


def test_bad_coverage_file_lookup(sham_cov_dir, expected_bins, expected_chroms):
    cp = FSCoverageProvider(sham_cov_dir)
    for bad_bin in ['bin_foo', 'bin_bar']:
        for chrom in expected_chroms:
            assert(cp.lookup_coverage_path(bad_bin, chrom) is None)

    for cbin in expected_bins:
        for bad_chrom in ['foo', 'bar', 'baz', 'duq']:
            assert(cp.lookup_coverage_path(cbin, bad_chrom) is None)


def test_nonexistant_coverage(sham_cov_dir, expected_bins):
    cp = FSCoverageProvider(sham_cov_dir)

    bad_bin_result = cp.coverage('bad_bin', '11', 100, 2000)
    bad_chr_result = cp.coverage(expected_bins[0], 'bad_chrom', 100, 2000)

    assert(isinstance(bad_bin_result, list))
    assert(len(bad_bin_result) == 0)
    assert(isinstance(bad_chr_result, list))
    assert(len(bad_chr_result) == 0)

def test_load_coverage(mocker, sham_cov_dir, expected_bins, expected_chroms):
    # Mock TabixFile.fetch
    sham_coverage = [('11', 1, 10, '{"mean": 10}'),
                     ('11', 11, 20, '{"mean": 9.9}'),
                     ('11', 21, 100, '{"mean": 20.1}')]

    attrs = {'fetch.return_value': sham_coverage}
    tabix_mock = mocker.Mock(TabixFile, **attrs)

    result = FSCoverageProvider.load_coverage_dicts(tabix_mock, '11', 1, 100)
    assert(isinstance(result, list))
    assert(len(result) == len(sham_coverage))

    for item in result:
        assert(isinstance(item, dict))


def test_coverage_trailing_slash(sham_cov_dir):
    sham_dir_trailing_slash = sham_cov_dir + '/'
    sham_dir_without_trailing_slash = sham_cov_dir

    cp_no_slash = FSCoverageProvider(sham_dir_without_trailing_slash)
    cp_from_slash = FSCoverageProvider(sham_dir_trailing_slash)

    warnings_no_slash = cp_no_slash.evaluate_catalog()
    warnings_from_slash = cp_from_slash.evaluate_catalog()

    assert(len(warnings_no_slash) == 0)
    assert(len(warnings_from_slash) == 0)
