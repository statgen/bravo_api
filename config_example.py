import os.path

# Required configuration
MONGO_URI = 'mongodb://localhost:27017/bravo-demo'
BRAVO_API_PAGE_LIMIT = 10000

BASE_DIR = os.path.join(os.sep, 'var', 'local', 'bravo', 'data', 'runtime')
COVERAGE_DIR = os.path.join(BASE_DIR, 'coverage')
SEQUENCES_DIR = os.path.join(BASE_DIR, 'crams')
SEQUENCES_CACHE_DIR = os.path.join(BASE_DIR, 'cache')
REFERENCE_SEQUENCE = os.path.join(BASE_DIR, 'reference', 'chr11_hs38DH.fa')

# Optional configuration
LOGIN_DISABLED = True
SESSION_SECRET = b'deadbeef0123456789'
CORS_ORIGINS = ['http://localhost:8080']

# Config for using Google OAuth
GOOGLE_CLIENT_ID = "your google oauth client id"
GOOGLE_CLIENT_SECRET = "your google oauth client secret"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
