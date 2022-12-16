import pytest

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
