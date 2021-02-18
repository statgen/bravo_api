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

Do `python -m pytest` will add the current directory to `sys.path`.
Do not `pytest` as that will not allow the current testing setup to find the bravo modules.

Existing tests are integration tests.  
Will be marked using `@pytest.mark.integration` decorator to differentiate from unit tests.


# Bravo UI
