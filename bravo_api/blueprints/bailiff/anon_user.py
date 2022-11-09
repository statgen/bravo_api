from flask_login import AnonymousUserMixin


class BravoAnonUser(AnonymousUserMixin):
    @property
    def agreed_to_terms(self):
        return False
