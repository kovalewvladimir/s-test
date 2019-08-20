import datetime

import mongoengine as db
from bson.objectid import ObjectId
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from config import SECRET_KEY


class Jokes(db.EmbeddedDocument):
    joke_id = db.ObjectIdField(required=True, default=ObjectId, primary_key=True)
    joke = db.StringField(required=True)


class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    jokes = db.EmbeddedDocumentListField(Jokes, default=[])

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': str(self.id)})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        try:
            user = User.objects.get(id=data['id'])
        except db.queryset.DoesNotExist:
            user = None
        return user


class ConnectionApplication(db.Document):
    date_connection = db.DateTimeField(
        default=datetime.datetime.utcnow)
