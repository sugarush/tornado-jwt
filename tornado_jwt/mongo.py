import jwt

from tornado import gen

from . auth import Authenticator


class MongoDBAuthenticator(Authenticator):

    def validate(self, username, password=None):
        pass

    @gen.coroutine
    def find(self, username):
        self.validate(username)
        users = self.settings['api_db'].users
        result = yield users.find_one({ 'username': username })
        raise gen.Return(result)

    @gen.coroutine
    def login(self, username, password):
        self.validate(username, password)
        secret = self.settings['secret']
        users = self.settings['api_db'].users
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
        self.validate(username, password)
        users = self.settings['api_db'].users
        result = yield users.insert_one({
            'username': username,
            'password': self.encrypt(password),
        })
        raise gen.Return(result)
