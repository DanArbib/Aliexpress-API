from flask import Flask
import os
from flask_cors import CORS
from dotenv import load_dotenv

# flask --app run --debug run --port 5000 --host 192.168.1.10

load_dotenv()


# App config
app = Flask(__name__)
app.app_context().push()
cors = CORS(app, resources={
    r"/api/*": {
        "origins": "http://192.168.1.10:3000",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "headers": ["Content-Type", "Authorization"]
    }
})

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Import routes
from app import routes

