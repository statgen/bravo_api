# Bravo API
Python web application using Flask.

Run on localhost:9099 in development.

Requires mongo db running?

Minimum data backing to avoid error on start:
```
data/
├── cache
└── crams
    └── demo
        ├── sequences
        ├── variant_map.tsv.gz
        └── variant_map.tsv.gz.tbi
```

## Running locally with sham data
Convenience to get application running without having to download external data and run it through a pipeline.
Sham data uses chr77 so as to be obviously a demo.

### Create sham data on disk
Run `make_data.py` to create a data directory in the shape that is used in production:
```
data
├── cache
├── coverage
│   └── bin_1
│       ├── coverage.json.gz
│       └── coverage.json.gz.tbi
├── crams
│   └── demo
│       ├── sequences
│       │   ├── reads.cram
│       │   └── reads.cram.crai
│       ├── variant_map.tsv.gz
│       └── variant_map.tsv.gz.tbi
└── reference
    ├── demoChr.fa
    └── demoChr.fa.fai
```

## Create sham data in mongo

Run `make_mongo.py` to create sham records in running mongo instance.

Examine the collection list and record structure
```sh
mongo bravo-demo --norc --eval 'db.getCollectionNames()'
mongo bravo-demo --norc --eval 'db.getCollectionNames().reduce((acc,cur)=>{acc[cur]=db[cur].findOne(); return acc}, {})'
```

## Testing

Do `python -m pytest` as it will add the current directory to `sys.path`.
Do not `pytest` as that will not allow the current testing setup to find the bravo modules.

Existing tests are integration tests.  
They depend on a particular data set and are marked with `@pytest.mark.integration` decorator to differentiate from unit tests.
Test non-integration tests with `python -m pytest -m 'not integration'`

## Data Pipelines

Originally located in the [Bravo repository](https://github.com/statgen/bravo.git).
Consists of three [Nextflow](https://nextflow.io) pipelines.
1. VCF annoted using Variant Effect Predictor (VEP) tool.
    - input: VCF or BCF files
2. Prepare minimized BAM files for IGV.js viewer which appears on the Bravo page for variants.
    - input: BAM or CRAM files
3. Prepare sequence depth histogram which appears on the Bravo pages for regions and genes.
    - input: BAM or CRAM files

### 1st pipeline
Takes input VCF or BCF files which can be chunked by chromosome or region.
Subsets the reads by individual to exclude those that have not consented to have their data used.
Output VCFs of each step are the inputs of the subsequent step.

1. Compute INFO fields and emit new VCF:
    - AC: allele count
    - AN: allele number
    - N: number of individuals
    - Depth histogram
2. Run VEP tool on each new VCF appending new INFO field:
    - CSQ: functional effect annotations
3. Add [CADD variant scores](https://cadd.gs.washington.edu/download) to VCFs INFO.
4. Compute and add percentiles for each variant quality metric to VCFs INFO.
5. Concatenate all VCFs into 1 VCF per chromosome
     
Setup of VEP tools described in this [repo](https://github.com/CERC-Genomic-
Medicine/vep_pipeline).


### 2nd pipeline
Sequences workflow to prepare BAM files for use with IGV.js viewer.

### 3rd pipeline
Coverage workflow to generate data for histogram visualization.
