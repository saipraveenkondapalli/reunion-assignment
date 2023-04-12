import os

from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# MongoDB configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask',
    'host': os.environ.get('REUNION_DB'),
}

db = MongoEngine(app)


