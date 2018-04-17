import jwt

from tornado import gen

from . auth import Authenticator


class MongoDBAuthenticator(Authenticator):

    def initialize(self, **kargs):
        super(Authenticator, self).initialize(**kargs)
        self.database = kargs.get('database')

    @gen.coroutine
    def find(self, username):
        users = self.database.users
        result = yield users.find_one({ 'username': username })
        raise gen.Return(result)

    @gen.coroutine
    def login(self, username, password):
        secret = self.settings['secret']
        users = self.database.users
        payload = yield users.find_one({
            'username': username,
            'password': self.encrypt(password)
        }, {
            'username': 1
        })
        if payload:
            payload['_id'] = str(payload['_id'])
            raise gen.Return(self.token(payload))

    @gen.coroutine
    def create(self, username, password):
        users = self.database.users
        result = yield users.insert_one({
            'username': username,
            'password': self.encrypt(password),
        })
        raise gen.Return(result)
