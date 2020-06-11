from pathlib import Path
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

UPLOAD_FOLDER = './audios'

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
CORS(app)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 35 * 1024 * 1024

app.jinja_env.line_statement_prefix = '#'

