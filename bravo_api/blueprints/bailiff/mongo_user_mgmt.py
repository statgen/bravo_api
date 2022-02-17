"""@package Mongo User Managment
Use mongo for persisting users.
"""
from bravo_api.models.database import mongo
import pymongo.errors
from .user_mgmt import UserMgmt
from .user import User


class MongoUserMgmt(UserMgmt):
    def mongo_doc_to_user(self, mongodoc):
        if mongodoc is None:
            return None
        return User(mongodoc.user_id, mongodoc.agreed_to_terms)

    def user_to_mongodoc(self, user):
        return {'user_id': user.get_id(), 'agreed_to_terms': user.agreed_to_terms}

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
        self.save(User(user_id))

    def update_agreed_to_terms(self, user):
        user.agreed_to_terms = True
        self.save(user)
