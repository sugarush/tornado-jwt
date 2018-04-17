import jwt, hashlib, sys

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

    def validate(self, username, password):
        return True

    def encrypt(self, password):
        return hashlib.sha512(password.encode('utf-8')).hexdigest()

    def token(self, data):
        return jwt.encode(data, self.settings['secret'],
            algorithm='HS256')

    @gen.coroutine
    def post(self):
        try:
            username = self.body.get('username')
            password = self.body.get('password')
            if not self.validate(username, password):
                self.send_error(400,
                    reason='unacceptable username or password'
                )
            elif username and password:
                token = yield self.login(username, password)
                if not token:
                    self.send_error(401, reason='invalid username or password')
                else:
                    self.send_json(200, {
                        'message': 'authenticated',
                        'token': token.decode('utf-8'),
                    })
            else:
                self.send_error(401, reason='invalid authorization request')
        except Exception as error:
            self.send_error(401, reason=str(error), exc_info=sys.exc_info())

    @gen.coroutine
    def put(self):
        try:
            username = self.body.get('username')
            password = self.body.get('password')
            if not self.validate(username, password):
                self.send_error(400,
                    reason='unacceptable username or password'
                )
            elif username and password:
                exists = yield self.find(username)
                if exists:
                    self.send_error(401, reason='username already exists')
                else:
                    created = yield self.create(username, password)
                    if created:
                        token = yield self.login(username, password)
                        if token:
                            self.send_json(201, {
                                'message': 'created',
                                'token': token.decode('utf-8')
                            })
                        else:
                            self.send_error(401,
                                reason='user created, authentication failed')
                    else:
                        self.send_error(401, reason='failed to create user')
            else:
                self.send_error(401, reason='invalid authorization request')
        except Exception as error:
            self.send_error(401, reason=str(error), exc_info=sys.exc_info())


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
                except Exception as error:
                    self.send_error(401, reason='failed to decode token')
            else:
                self.send_error(401, reason='invalid authorization request')
        else:
            self.send_error(401, reason='authorization header missing')
