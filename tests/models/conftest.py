import pytest
import os.path
from testfixtures import TempDirectory
from pathlib import Path


# Fixture for testing coverage directory structure
# 5 subdirectories with 2 indexed chromosomes each.
@pytest.fixture()
def mock_coverage_dir():
    with TempDirectory() as dir:
        for bindir in ['full', 'bin_1.00', 'bin_0.25', 'bin_0.50', 'bin_0.75']:
            dirpath = dir.makedir(bindir)
            Path(os.path.join(dirpath, 'chr1.json.gz')).touch()
            Path(os.path.join(dirpath, 'chr1.json.gz.tbi')).touch()
            Path(os.path.join(dirpath, 'chr2.json.gz')).touch()
            Path(os.path.join(dirpath, 'chr2.json.gz.tbi')).touch()
        yield dir
