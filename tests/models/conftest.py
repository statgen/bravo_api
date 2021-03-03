import pytest
import os.path
from testfixtures import TempDirectory
from pathlib import Path


# Fixture for testing coverage directory structure
# 5 subdirectories with 2 files each.
@pytest.fixture()
def mock_coverage_dir():
    with TempDirectory() as dir:
        for bindir in ['full', 'bin_1', 'bin_25e-2', 'bin_50e-2', 'bin_75e-2']:
            dirpath = dir.makedir(bindir)
            Path(os.path.join(dirpath, 'foo.json.gz')).touch()
            Path(os.path.join(dirpath, 'bar.json.gz')).touch()
        yield dir
