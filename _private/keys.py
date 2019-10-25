
"""
This file contains secret/sensitive information such as access keys of APIS used for this app.
Hence this file will not be pushed to github or shared with anyone.
"""

# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'SANATHANA-DHARMA-APP'

ADMIN_LIST = {
	"kiran@suryakiran.com": "Surya Kiran",
	"2maxdc@gmail.com": "Carp-Bezverhnii Maxim",
	"charming30@gmail.com": "Charming Thirty"
}

#Google oauth credentials
#GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
#GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_APPLICATION_CREDENTIALS = "/Users/suryakiran/code/sanathana-dharma/_private/sanathana-dharma-app-71a9d654e3e3.json"
GOOGLE_CLIENT_ID = "7158413011-tsmtcnbqec4dsvn2mjhrad50gouoe039.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "7bMpMDY0fV5UPW7c2xwNEs58"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

#Algolia search keys
ALGOLIA_APPLICATION_ID = "SSR6G43F45"
ALGOLIA_SEARCH_ONLY_API_KEY = "d3a70a9b4e7930c99317014d2a6ccb6f"
ALGOLIA_ADMIN_API_KEY = "572f32348c896b778a94b88eab64ad40"
