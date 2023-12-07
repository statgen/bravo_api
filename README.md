# Bravo API

The server side application of the BRowse All Variants Online (BRAVO) project.

## Installation
For running an instance of Bravo API, install as a package.
```
python -m pip install git+https://github.com/statgen/bravo_api.git@main
```
See [Development](#Development) section for developer installation.

## Running

```sh
#!/bin/sh

# Example run script for local development

# Activate venv if present.
[ -d 'venv' ] && source 'venv/bin/activate'

export FLASK_APP=bravo_api

# Confige file is relative to the instance directory.
export BRAVO_API_INSTANCE_DIR='/var/local/bravo/instance'
export BRAVO_API_CONFIG_FILE='config.py'

flask run --port 9090
```
Or use gunicorn in production instead of `flask run`
```sh
gunicorn -b 127.0.0.1:9090 -w 5 -k gevent "bravo_api:create_app()"
```

## Dependencies

### Runtime Data
The runtime data on disk needs to be present before running.

```
/var/local/bravo/data
└── runtime
    ├── cache
    ├── coverage
    ├── crams
    └── reference
```

The paths to the runtime data needs to be specified in the config.py
```py
BASE_DIR = os.path.join(os.sep, 'var', 'local', 'bravo', 'data', 'runtime')

COVERAGE_DIR = os.path.join(BASE_DIR, 'coverage')
SEQUENCES_DIR = os.path.join(BASE_DIR, 'crams')
SEQUENCES_CACHE_DIR = os.path.join(BASE_DIR, 'cache')
REFERENCE_SEQUENCE = os.path.join(BASE_DIR, 'reference', 'chr11_hs38DH.fa')
```

### MongoDB
MongoDB needs to be pupulated with the basis data prior to running the api.

```
/var/local/bravo/data/basis/
├── qc_metrics
│   └── metrics.json.gz
├── reference
│   ├── canonical_transcripts.tsv.gz
│   ├── gencode.v38.annotation.gtf.gz
│   ├── hgcn_genenames.tsv.gz
│   └── omim_ensembl_refs.tsv.gz
└── vcfs
    ├── chr11.bravo.vcf.gz
    └── chr11.bravo.vcf.gz.tbi
```

The package provides commands to load the basis data.
```sh
export BRAVO_API_CONFIG_FILE='/path/to/config.py'
venv/bin/flask load-genes \
  data/basis/reference/canonical_transcripts.tsv.gz \
  data/basis/reference/omim_ensembl_refs.tsv.gz \
  data/basis/reference/hgcn_genenames.tsv.gz \
  data/basis/reference/gencode.v38.annotation.gtf.gz

venv/bin/flask load-snv 2 data/basis/vcfs/*.vcf.gz

venv/bin/flask load-qc-metrics \
	data/basis/qc_metrics/metrics.json.gz
```

### Pysam S3 Support
The pysam wheel provided from pypi does not include S3 support.
Pysam needs to be build with the "--enable-s3" option.

```sh
HTSLIB_CONFIGURE_OPTIONS="--enable-s3"
pip install pysam --force-reinstall --no-binary :all:
```

## Development
Checkout and install as editable package with development and testing extras.
```
git clone https://github.com/statgen/bravo_api.git
cd bravo_api
python -m pip install -e .[dev,test]
```

### Testing
When installed as editable package, run `pytest` from root dir or anywhere in tests dir.

```
# Run the tests
pytest
```

Top level testconf.py in the tests directory prevents marked tests from running.
In order to run marked tests in addition to the unmarked, provide a match expression.

```
# Run integration tests
pytest -m 'integration'
```

#### Autorunning tests
A low overhead (not constantly polling) method of running `pytest` anytime a .py file is changed
can be achieved using `fd` and `entr` in a separate terminal.
Only thing this won't pick up is new files.

```sh
fd '.*\.py$' | entr -c pytest
```

See [notes.md](notes.md)
