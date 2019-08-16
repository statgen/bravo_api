PROXY = True # True if app is proxied by Apache or similar
SECRET_KEY = b'' # secret key for Flask app session for web browser
URL_PREFIX = ''
MONGO_URI = 'mongodb://' # mongodb://<host>:<port>/<database>
BRAVO_API_URI = 'http://' # needed by BRAVO browser
GZIP_COMPRESSION = True
GOOGLE_OAUTH_CLIENT_SECRET = '' # path to JSON file with Google OAuth2 client secret

# For home page and navigation bar
SUBTITLE = ''
DATASET_SHORT_NAME = ''
ARCHIVES = []

# Fill these variables if you want to provide downloads
DOWNLOADS = False
DOWNLOAD_CHROMOSOMES_VCF = {} # e.g. { '21': ['100 MB', '/data/vcfs/chr21.vcf.gz'], '22': ['100 MB', '/data/vcfs/chr22.vcf.gz'] }

GOOGLE_ANALYTICS_TRACKING_ID = ''
