import os.path

# Required configuration
MONGO_URI = 'mongodb://localhost:27017/bravo-demo'
BRAVO_API_PAGE_LIMIT = 10000

# runtime directory in the unpacked vignette or from completed data prep run.
BASE_DIR = os.path.join(os.sep, 'var', 'local', 'bravo', 'data', 'runtime')

# File system path or S3 path to SNV coverage and crams directories
COVERAGE_DIR = os.path.join(BASE_DIR, 'coverage')
SEQUENCES_DIR = os.path.join(BASE_DIR, 'crams')

REFERENCE_SEQUENCE = os.path.join(BASE_DIR, 'reference', 'hs38DH.fa')
SEQUENCES_CACHE_DIR = os.path.join(BASE_DIR, 'cache')

# File system path or S3 path to structural variant (SV) sequences and index
STRUCTVAR_SEQUENCES_DIR = os.path.join(BASE_DIR, 'structvar')

# Optional configuration
LOGIN_DISABLED = True
SESSION_SECRET = b'deadbeef0123456789'
CORS_ORIGINS = ['http://localhost:8080']

# Config for using Google OAuth
GOOGLE_CLIENT_ID = "your google oauth client id"
GOOGLE_CLIENT_SECRET = "your google oauth client secret"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# File system path to public directories or S3 bucket path
PUBVCFS_DIR = os.path.join(os.sep, 'var', 'local', 'bravo', 'data', 'runtime', 'pubvcfs')

# When specified, will restruct authorized users to a single domain (empty string accepts all)
USER_DOMAIN_PERMITTED = ""
