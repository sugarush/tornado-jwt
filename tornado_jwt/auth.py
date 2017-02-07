import jwt, hashlib

from abc import ABCMeta, abstractmethod

from tornado import gen
from tornado_json import JSONHandler


class Authenticator(JSONHandler):

    __metaclass__ = ABCMeta

    @abstractmethod
    def find(self, username):
        pass

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def create(self, username, password):
        pass

    def encrypt(self, password):
        return hashlib.sha512(password).hexdigest()

    @gen.coroutine
    def post(self):
        try:
            user = self.decode(self.request.body)
            if user.get('username') and user.get('password'):
                token = yield self.login(user['username'], user['password'])
                if not token:
                    self.send_error(401, reason='invalid username or password')
                else:
                    self.send_json(200, {
                        'success': 'authenticated',
                        'token': token,
                    })
            else:
                self.send_error(401, reason='invalid authorization request')
        except Exception, error:
            self.send_error(401, reason=error.message)

    @gen.coroutine
    def put(self):
        try:
            user = self.decode(self.request.body)
            if user.get('username') and user.get('password'):
                exists = yield self.find(user['username'])
                if exists:
                    self.send_error(401, reason='username already exists')
                else:
                    created = yield self.create(user['username'], user['password'])
                    if created:
                        token = yield self.login(user['username'], user['password'])
                        if token:
                            self.send_json(201, {
                                'success': 'created',
                                'token': token
                            })
                        else:
                            self.send_error(401,
                                reason='user created, authentication failed')
                    else:
                        self.send_error(401, reason='failed to create user')
            else:
                self.send_error(401, reason='invalid authorization request')
        except Exception, error:
            self.send_error(401, reason=error.message)


class Authenticated(JSONHandler):

    options = {
        'verify_signature': True,
        'verify_exp': True,
        'verify_nbf': False,
        'verify_iat': True,
        'verify_aud': False
    }

    def prepare(self):
        super(Authenticated, self).prepare()
        auth = (self.request.headers.get('Authorization') or '').split()
        if auth:
            if auth[0].lower() == 'bearer':
                try:
                    token = auth[1]
                    secret = self.settings['secret']
                    self.current_user = jwt.decode(token, secret,
                        options=self.options, algorithms=['HS256'])
                except Exception, error:
                    self.send_error(401, reason='failed to decode token')
            else:
                self.send_error(401, reason='invalid authorization request')
        else:
            self.send_error(401, reason='authorization header missing')
