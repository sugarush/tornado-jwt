import jwt

from tornado import gen

from . auth import Authenticator


class MemoryDB(object):

    def __init__(self):
        self.users = { }

    def find(self, username):
        return self.users.get(username)

    def create(self, username, password):
        self.users[username] = password


class MemoryAuthenticator(Authenticator):

    def initialize(self, **kargs):
        super(Authenticator, self).initialize(**kargs)
        self.database = kargs.get('database')

    def validate(self, username, password=None):
        pass

    @gen.coroutine
    def find(self, username):
        self.validate(username)
        encrypted_password = self.database.find(username)
        raise gen.Return(encrypted_password)

    @gen.coroutine
    def login(self, username, password):
        self.validate(username, password)
        payload = None
        encrypted_password = self.database.find(username)
        if encrypted_password and encrypted_password == self.encrypt(password):
            payload = self.token({ 'username': username })
        raise gen.Return(payload)

    @gen.coroutine
    def create(self, username, password):
        self.validate(username, password)
        self.database.create(username, self.encrypt(password))
        raise gen.Return(True)
