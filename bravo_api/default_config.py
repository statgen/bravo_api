# Session and login remember_me cookie flags
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True

# Default Optional configuration
LOGIN_DISABLED = True
SESSION_SECRET = b'deadbeef0123456789'
CORS_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080']

GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Use the following key to only allow users from a single domain
#  Leave undefined or "" to allow users to authenticate from all domains
# USER_DOMAIN_PERMITTED = "example.com"
