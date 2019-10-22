
"""
This file contains all of the configuration values for the application.
"""

import os

# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'SANATHANA-DHARMA-APP'

PROJECT_ID = 'sanathana-dharma-app'

DATA_BACKEND = 'datastore'

LANGUAGES = {
	"ENG": "English",
	"SAN": "Sanskrit",
	"HIN": "Hindi",
	"KAN": "Kannada"
}

ADMIN_LIST = {
	"kiran@suryakiran.com": "Surya Kiran",
}

#Google oauth credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
