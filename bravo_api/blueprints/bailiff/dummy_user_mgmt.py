"""@package Dummy User Managment
In memory list of users for development purposes only.
"""
from .user_mgmt import UserMgmt
from .user import User
from datetime import datetime


class DummyUserMgmt(UserMgmt):
    DUMMY_USERS = set()
    AUTH_LOG = list()
    user_klass = User

    def load(self, user_id):
        for u in DummyUserMgmt.DUMMY_USERS:
            if u.get_id() == user_id:
                return u
        return None

    def save(self, user):
        DummyUserMgmt.DUMMY_USERS.discard(user)
        DummyUserMgmt.DUMMY_USERS.add(user)
        return(user)

    def create_by_id(self, user_id):
        user = self.save(self.user_klass(user_id))
        return(user)

    def update_agreed_to_terms(self, user):
        user.agreed_to_terms = True
        user.agreed_date = datetime.today()
        return(self.save(user))

    def log_auth(self, user):
        entry = (user.get_id(), datetime.today())
        self.AUTH_LOG.append(entry)

    @classmethod
    def set_user_class(cls, user_class):
        cls.user_klass = user_class
