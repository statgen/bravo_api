"""@package Bravo User
Represent a user of the BRAVO site.
"""
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, email, agreed_to_terms=False):
        self.id = email
        self.agreed_to_terms = False
