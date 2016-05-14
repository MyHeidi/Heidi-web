import os

SECRET_KEY = None
APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
DEBUG = False
DEBUG_TB_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

YELP_CONSUMER_KEY = None
YELP_CONSUMER_SECRET = None
YELP_TOKEN = None
YELP_TOKEN_SECRET = None

try:
    from local_settings import *
except ImportError:
    pass
