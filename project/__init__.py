from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'

# MongoDB configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask',
    'host': 'mongodb+srv://saipraveenkondapalli0:0Ul0zHoeuB87yxgL@cluster0.v80uxg8.mongodb.net/reunion?retryWrites=true&w=majority'
}

db = MongoEngine(app)


