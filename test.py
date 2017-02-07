from tornado import testing, web, gen
from tornado.escape import json_encode, json_decode
from tornado.httputil import HTTPHeaders

from copy import deepcopy

from tornado_jwt import MongoDBAuthenticator, Protected


class CollectionMock(object):

    def __init__(self):
        self.data = [ ]

    @gen.coroutine
    def find_one(self, query, projection={ }):
        for item in self.data:
            if all(map(lambda (k, v): item.get(k) == v, query.items())):
                raise gen.Return(deepcopy(item))

    @gen.coroutine
    def insert_one(self, item):
        item['_id'] = len(self.data)
        self.data.append(item)
        raise gen.Return(deepcopy(item))

class MongoDBMock(object):

    def __init__(self):
        self.users = CollectionMock()


class ProtectedEndpoint(Protected):

    def get(self):
        self.write(json_encode({
            'success': 'it worked'
        }))


class TestAuthenticator(testing.AsyncHTTPTestCase):

    def get_app(self):
        self.body = { "username": "user", "password": "password" }
        self.db = MongoDBMock()

        settings = {
            'secret': 'secret',
            'api_db': self.db,
        }

        return web.Application([
            (r'/auth', MongoDBAuthenticator),
            (r'/v1/protected', ProtectedEndpoint)
        ], **settings)

    def test_authenticator_create_user(self):
        # create user
        response = self.fetch('/auth', method='PUT', body=json_encode(self.body))
        self.assertIn('success', response.body)
        self.assertIn('token', response.body)

        # try to create dupilcate user
        response = self.fetch('/auth', method='PUT', body=json_encode(self.body))
        self.assertIn('error', response.body)

        # try to create user without username
        _body = deepcopy(self.body)
        del(_body['username'])
        response = self.fetch('/auth', method='PUT', body=json_encode(_body))
        self.assertIn('error', response.body)

        # try to create user without password
        _body = deepcopy(self.body)
        del(_body['password'])
        response = self.fetch('/auth', method='PUT', body=json_encode(_body))
        self.assertIn('error', response.body)

        # try to create user without username or password
        _body = deepcopy(self.body)
        del(_body['username'])
        del(_body['password'])
        response = self.fetch('/auth', method='PUT', body=json_encode(_body))
        self.assertIn('error', response.body)

    def test_authenticator_login_user(self):
        # create user
        response = self.fetch('/auth', method='PUT', body=json_encode(self.body))
        self.assertIn('success', response.body)
        self.assertIn('token', response.body)

        # login as user
        response = self.fetch('/auth', method='POST', body=json_encode(self.body))
        self.assertIn('success', response.body)
        self.assertIn('token', response.body)

        # try to login witout username
        _body = deepcopy(self.body)
        del(_body['username'])
        response = self.fetch('/auth', method='POST', body=json_encode(_body))
        self.assertIn('error', response.body)

        # try to login witout password
        _body = deepcopy(self.body)
        del(_body['password'])
        response = self.fetch('/auth', method='POST', body=json_encode(_body))
        self.assertIn('error', response.body)

        # try to login witout password
        _body = deepcopy(self.body)
        del(_body['username'])
        del(_body['password'])
        response = self.fetch('/auth', method='POST', body=json_encode(_body))
        self.assertIn('error', response.body)

    def test_authenticated_request(self):
        # create user
        response = self.fetch('/auth', method='PUT', body=json_encode(self.body))
        self.assertIn('success', response.body)
        self.assertIn('token', response.body)
        token = json_decode(response.body)['token']

        # use token for authenticated request
        response = self.fetch('/v1/protected', method='GET', headers=HTTPHeaders({
            'Authorization': 'Bearer %s' % token
        }))
        self.assertIn('success', response.body)

        # don't use token for unauthorized request
        response = self.fetch('/v1/protected', method='GET')
        self.assertIn('error', response.body)
