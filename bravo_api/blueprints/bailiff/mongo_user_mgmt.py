"""@package Mongo User Managment
Use mongo for persisting users.
"""
import pymongo.errors
from datetime import datetime
from bravo_api.models.database import mongo
from .user_mgmt import UserMgmt
from .user import User


class MongoUserMgmt(UserMgmt):
    def __init__(self, mongo_client, user_class=User):
        self.mongo = mongo_client
        self.user_klass = user_class

    def mongo_doc_to_user(self, mongodoc):
        if mongodoc is None:
            return None
        return self.user_klass(mongodoc['user_id'], mongodoc['agreed_to_terms'])

    def user_to_mongodoc(self, user):
        return {'user_id': user.get_id(), 'agreed_to_terms': user.agreed_to_terms,
                'agreed_date': user.agreed_date}

    def load(self, user_id):
        result = mongo.db.users.find_one({'user_id': user_id}, projection={'_id': False})
        return self.mongo_doc_to_user(result)

    def save(self, user):
        try:
            mongo.db.users.replace_one({'user_id': user.id}, self.user_to_mongodoc(user),
                                       upsert=True)
        except pymongo.errors.WriteError:
            return None
        return user

    def create_by_id(self, user_id):
        user = self.save(self.user_klass(user_id))
        return(user)

    def update_agreed_to_terms(self, user):
        user.agreed_to_terms = True
        user.agreed_date = datetime.today()
        return(self.save(user))

    def log_auth(self, user):
        entry = {'user_id': user.get_id(), 'timestamp': datetime.now()}
        mongo.db.auth_log.insert_one(entry)
