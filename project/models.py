import datetime

from . import db


class User(db.Document):
    id = db.SequenceField(primary_key=True)
    name = db.StringField(required=True)
    email = db.StringField(required=True)
    password = db.StringField(required=True)
    followers = db.ListField(db.ReferenceField('User'))
    following = db.ListField(db.ReferenceField('User'))


class Comment(db.EmbeddedDocument):
    id = db.StringField(primary_key=True)
    user = db.ReferenceField(User)
    text = db.StringField(required=True)


class Post(db.Document):
    id = db.SequenceField(primary_key=True)
    title = db.StringField(required=True)
    description = db.StringField(required=True)
    likes = db.ListField(db.ReferenceField(User))
    created_time = db.DateTimeField(default = datetime.datetime.utcnow())
    comments = db.ListField(db.EmbeddedDocumentField(Comment))
    author = db.ReferenceField(User)

