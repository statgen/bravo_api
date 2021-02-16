# True if app is proxied by Apache or similar
PROXY = False
# secret key for Flask app sessions
SECRET_KEY = b'deadbeef'
URL_PREFIX = ''
MONGO_URI = 'mongodb://localhost:27017/bravo-demo'  # mongodb://<host>:<port>/<database>
# Base API URL to call
BRAVO_API_URI = 'http://localhost:9099'
GZIP_COMPRESSION = True
GOOGLE_OAUTH_CLIENT_SECRET = '' # path to JSON file with Google OAuth2 client secret

# For home page and navigation bar
SUBTITLE = ''
DATASET_SHORT_NAME = ''
ARCHIVES = []

# Fill these variables if you want to provide downloads
DOWNLOADS = False
DOWNLOAD_LABEL = 'Downloads'
DOWNLOAD_CHROMOSOMES_VCF = {} # e.g. { '21': ['100 MB', '/data/vcfs/chr21.vcf.gz'], '22': ['100 MB', '/data/vcfs/chr22.vcf.gz'] }
DOWNLOAD_CHROMOSOMES_COVERAGE = {} # e.g. { '21': ['300 MB', '/data/coverage/chr21.txt.gz'], '22': ['400 MB', '/data/coverage/chr22.txt.gz'] }

GOOGLE_ANALYTICS_TRACKING_ID = ''
