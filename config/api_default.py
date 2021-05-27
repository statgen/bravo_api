import os.path

MONGO_URI = 'mongodb://localhost:27017/bravo-demo'  # mongodb://<host>:<port>/<database>
BRAVO_API_PAGE_LIMIT = 10000
GZIP_COMPRESSION = True

# base directory for data on disk. E.g. /data/bravo
BASE_DIR = os.path.join(os.sep, 'data', 'bravo')

# directory with coverage files
COVERAGE_DIR = os.path.join(BASE_DIR, 'coverage')

# directory containing variant map and sequences/ dir
#  Contained sequences dir expected to have with CRAM files
SEQUENCES_DIR = os.path.join(BASE_DIR, 'crams')

# directory for the runtime cached BAM/CRAM files
SEQUENCES_CACHE_DIR = os.path.join(BASE_DIR, 'cache')

# path to reference sequence for cram files.  Assumes corresponding .fai exists next to .fa file
REFERENCE_SEQUENCE = os.path.join(BASE_DIR, 'reference', 'hg38DH.fa')
