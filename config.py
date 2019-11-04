
"""
This file contains all of the configuration values for the application.
"""

import os


PROJECT_ID = 'sanathana-dharma-app'

DATA_BACKEND = 'datastore'

DICT_SEARCH_INDEXES = {
	"TREE": "TREE",
}


DICT_LANGUAGES = {
	"ENG": "English",
	"SAN": "Sanskrit",
	"HIN": "Hindi",
	"KAN": "Kannada"
}

DICT_CONTENT_TYPE = {
	"10": "Source",
	"11": "Bhashya",
	"12": "Vyakhya",
	"13": "Varthikam",
	"14": "Tippani"
}


DICT_SOURCEDOCS = {
	"101": "Source",
	"102": "Doc1",
	"103": "Doc2",
	"104": "Doc3"
}

#Google oauth credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
