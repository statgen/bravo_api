"""@package Bravo User
User class restricting valid users to a that of a single domain.
"""
from flask_login import UserMixin


class DomainUser(UserMixin):
    permitted_domain = "example.com"

    def __init__(self, email, agreed_to_terms=False):
        self.id = email
        self.domain = DomainUser.parse_domain(email)
        self.agreed_to_terms = agreed_to_terms
        self.agreed_date = None

    @property
    def is_authenticated(self):
        return self.domain == self.permitted_domain

    @staticmethod
    def parse_domain(email):
        if "@" not in email or email == "":
            return ""
        return email.split("@", maxsplit=1)[-1]

    @classmethod
    def set_permitted_domain(cls, domain):
        cls.permitted_domain = domain
