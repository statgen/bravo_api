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

## Coverage data
Coverage data is four column tab delimted: `chr\tstart\tend\tdata`.
The data column (4th) contains JSON data with coverage statistics for the start-end range.

```tsv
11      5220498 5220498 {"chrom":"11","start":5220498,"end":5220498,"mean":36.66,"median":36,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.9,"30":0.8,"50":0.06,"100":0}
11      5220499 5220499 {"chrom":"11","start":5220499,"end":5220499,"mean":35.8,"median":35,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.92,"30":0.78,"50":0.08,"100":0}
11      5220500 5220500 {"chrom":"11","start":5220500,"end":5220500,"mean":36.72,"median":36,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.94,"30":0.78,"50":0.1,"100":0}
11      5220501 5220501 {"chrom":"11","start":5220501,"end":5220501,"mean":36.02,"median":35,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.92,"30":0.78,"50":0.08,"100":0}
11      5220502 5220502 {"chrom":"11","start":5220502,"end":5220502,"mean":36.36,"median":36,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.94,"30":0.78,"50":0.08,"100":0}
11      5220503 5220503 {"chrom":"11","start":5220503,"end":5220503,"mean":35.14,"median":35,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.94,"30":0.76,"50":0.06,"100":0}
11      5220504 5220504 {"chrom":"11","start":5220504,"end":5220504,"mean":36.64,"median":35,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.94,"30":0.8,"50":0.08,"100":0}
11      5220505 5220505 {"chrom":"11","start":5220505,"end":5220505,"mean":36.78,"median":36.5,"1":1,"5":1,"10":1,"15":1,"20":1,"25":0.94,"30":0.86,"50":0.08,"100":0}
11      5220506 5220506 {"chrom":"11","start":5220506,"end":5220506,"mean":36.8,"median":35.5,"1":1,"5":1,"10":1,"15":1,"20":1,"25":0.94,"30":0.84,"50":0.08,"100":0}
11      5220507 5220507 {"chrom":"11","start":5220507,"end":5220507,"mean":36.44,"median":35.5,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.94,"30":0.82,"50":0.1,"100":0}
11      5220508 5220508 {"chrom":"11","start":5220508,"end":5220508,"mean":36.38,"median":35,"1":1,"5":1,"10":1,"15":1,"20":1,"25":0.94,"30":0.84,"50":0.08,"100":0}
11      5220509 5220509 {"chrom":"11","start":5220509,"end":5220509,"mean":37.52,"median":36,"1":1,"5":1,"10":1,"15":1,"20":1,"25":0.94,"30":0.86,"50":0.1,"100":0}
11      5220510 5220510 {"chrom":"11","start":5220510,"end":5220510,"mean":36.56,"median":35,"1":1,"5":1,"10":1,"15":1,"20":0.98,"25":0.94,"30":0.84,"50":0.08,"100":0}
```
