from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'

# MongoDB configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask',
    'host': 'mongodb+srv://flask_mongo_db:qazwsxedc@cluster0.8qy3w5u.mongodb.net/Reunion?retryWrites=true&w=majority'
}

db = MongoEngine(app)
