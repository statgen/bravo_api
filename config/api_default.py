import os.path

MONGO_URI = 'mongodb://localhost:27017/bravo-demo'  # mongodb://<host>:<port>/<database>
BRAVO_API_PAGE_LIMIT = 10000
GZIP_COMPRESSION = True

# base directory for data on disk
BASE_DIR = os.path.abspath('data')

# directory with coverage files
COVERAGE_DIR = os.path.join('coverage')

# directory with BAM/CRAM sequence files
SEQUENCES_DIR = os.path.join('crams', 'demo')

# directory for the runtime cached BAM/CRAM files
SEQUENCES_CACHE_DIR = os.path.join('cache')

# path to reference sequence for cram files
REFERENCE_SEQUENCE = os.path.join('reference','demoChr.fa')
