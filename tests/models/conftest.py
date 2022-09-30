import pytest
import os.path
from testfixtures import TempDirectory
from pathlib import Path
from bravo_api.models import variants


# Fixture for testing coverage directory structure
# 5 subdirectories with 2 indexed chromosomes each.
@pytest.fixture()
def mock_coverage_dir():
    with TempDirectory() as dir:
        for bin_name in ['full', 'bin_1.00', 'bin_0.25', 'bin_0.50', 'bin_0.75']:
            dirpath = dir.makedir(bin_name)
            Path(os.path.join(dirpath, f'chr1.{bin_name}.tsv.gz')).touch()
            Path(os.path.join(dirpath, f'chr1.{bin_name}.tsv.gz.tbi')).touch()
            Path(os.path.join(dirpath, f'chr2.{bin_name}.tsv.gz')).touch()
            Path(os.path.join(dirpath, f'chr2.{bin_name}.tsv.gz.tbi')).touch()
        yield dir


@pytest.fixture()
def patch_variants_mongo(monkeypatch, mongodb):
    monkeypatch.setattr(variants, 'mongo', mongodb)
