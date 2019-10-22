import os
from flask import current_app, Flask, redirect, url_for, request

#Auth lib
import argparse
import treemgr
import config
import logging
import json
import utils

import os


from cgi import parse_qs
from datetime import datetime
import os
import string
import urllib


app = Flask(__name__)
app.config.from_object(config)
app.debug = True
app.testing = False

# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)

# Register the blueprint.
from treemgr.routes import mod
app.register_blueprint(treemgr.routes.mod, url_prefix='/admin')

# Add an error handler. This is useful for debugging the live application,
# however, you should disable the output of the exception for production
# applications.
@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500





# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
