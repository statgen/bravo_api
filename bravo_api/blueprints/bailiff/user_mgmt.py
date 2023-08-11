"""@package User Managment
Abstract class defining the responsibilities of user managment.
"""
from abc import ABC, abstractmethod


class UserMgmt(ABC):
    @abstractmethod
    def load(user_id):
        pass

    @abstractmethod
    def save(user):
        pass

    @abstractmethod
    def create_by_id(user_id):
        pass

    @abstractmethod
    def update_agreed_to_terms(user):
        pass

    @abstractmethod
    def log_auth(user):
        pass
