


# Load environment variables from .env
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from flask import Flask


app = Flask(__name__)
# Set a secret key for session management and flash
import os
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')


# Import and register the blueprint
from .routes import main
app.register_blueprint(main)
