import os

SECRET_KEY = None
APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

DEBUG = False
DEBUG_TB_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

SQLALCHEMY_DATABASE_URI = None
SQLALCHEMY_TRACK_MODIFICATIONS = False

SUGGESTION_CATEGORIES = ('restaurants', 'danceclubs', 'bars')
SUGGESTION_TERMS = ('italian', 'indian')

APN_TOKENS = []

UPLOADS_DEFAULT_DEST = os.path.join(APP_DIR, 'uploads')
UPLOADS_PHOTOS_DEST = os.path.join(UPLOADS_DEFAULT_DEST, 'photos')

APN_CERT_PATH = os.path.join(APP_DIR, 'secret', 'heidi.crt.pem')
APN_KEY_PATH = os.path.join(APP_DIR, 'secret', 'heidi.key.pem')

GOOGLE_MAPS_API_KEY = None

YELP_CONSUMER_KEY = None
YELP_CONSUMER_SECRET = None
YELP_TOKEN = None
YELP_TOKEN_SECRET = None

HOD_API_KEY = None

try:
    from local_settings import *
except ImportError:
    pass
