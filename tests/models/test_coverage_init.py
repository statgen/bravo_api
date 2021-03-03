import os.path
from bravo_api.models import coverage


# Ensure coverage file enumeration given a coverage directoy path with or without trailing slash.
def test_coverage_file_enumeration_no_trailing_slash(mock_coverage_dir):
    coverage_directory = mock_coverage_dir.path
    result = coverage.generate_coverage_files_metadata(coverage_directory)

    assert type(result) is list
    assert(len(result)) == 10
    assert(all(os.path.exists(cov_md['path']) for cov_md in result))


def test_coverage_file_enumeration_trailing_slash(mock_coverage_dir):
    coverage_directory = mock_coverage_dir.path + os.path.sep
    result = coverage.generate_coverage_files_metadata(coverage_directory)

    assert type(result) is list
    assert(len(result)) == 10
    assert(all(os.path.exists(cov_md['path']) for cov_md in result))
