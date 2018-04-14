from unittest import skip

from tornado import testing, web, gen
from tornado.escape import json_encode, json_decode
from tornado.httputil import HTTPHeaders

from copy import deepcopy

from tornado_jwt import MongoDBAuthenticator, MemoryAuthenticator, MemoryDB, Authenticated
from tornado_json import JSONHandler


class CollectionMock(object):

    def __init__(self):
        self.data = [ ]

    @gen.coroutine
    def find_one(self, query, projection={ }):
        for item in self.data:
            if all(map(lambda kv: item.get(kv[0]) == kv[1], query.items())):
                raise gen.Return(deepcopy(item))

    @gen.coroutine
    def insert_one(self, item):
        item['_id'] = len(self.data)
        self.data.append(item)
        raise gen.Return(deepcopy(item))


class MongoDBMock(object):

    def __init__(self):
        self.users = CollectionMock()


class AuthenticatedEndpoint(Authenticated):

    def get(self):
        self.write(json_encode({
            'success': 'it worked'
        }))


class Tests:

    def test_authenticator_create_user(self):
        # create user
        response = self.fetch('/auth', method='PUT',
            body=json_encode(self.body))
        self.assertIn('success', response.body.decode('utf-8'))
        self.assertIn('token', response.body.decode('utf-8'))

        # try to create dupilcate user
        response = self.fetch('/auth', method='PUT',
            body=json_encode(self.body))
        self.assertIn('error', response.body.decode('utf-8'))

        # try to create user without username
        _body = deepcopy(self.body)
        del(_body['username'])
        response = self.fetch('/auth', method='PUT',
            body=json_encode(_body))
        self.assertIn('error', response.body.decode('utf-8'))

        # try to create user without password
        _body = deepcopy(self.body)
        del(_body['password'])
        response = self.fetch('/auth', method='PUT',
            body=json_encode(_body))
        self.assertIn('error', response.body.decode('utf-8'))

        # try to create user without username or password
        _body = deepcopy(self.body)
        del(_body['username'])
        del(_body['password'])
        response = self.fetch('/auth', method='PUT',
            body=json_encode(_body))
        self.assertIn('error', response.body.decode('utf-8'))

    def test_authenticator_login_user(self):
        # create user
        response = self.fetch('/auth', method='PUT',
            body=json_encode(self.body))
        self.assertIn('success', response.body.decode('utf-8'))
        self.assertIn('token', response.body.decode('utf-8'))

        # login as user
        response = self.fetch('/auth', method='POST',
            body=json_encode(self.body))
        self.assertIn('success', response.body.decode('utf-8'))
        self.assertIn('token', response.body.decode('utf-8'))

        # try to login witout username
        _body = deepcopy(self.body)
        del(_body['username'])
        response = self.fetch('/auth', method='POST',
            body=json_encode(_body))
        self.assertIn('error', response.body.decode('utf-8'))

        # try to login witout password
        _body = deepcopy(self.body)
        del(_body['password'])
        response = self.fetch('/auth', method='POST',
            body=json_encode(_body))
        self.assertIn('error', response.body.decode('utf-8'))

        # try to login witout password
        _body = deepcopy(self.body)
        del(_body['username'])
        del(_body['password'])
        response = self.fetch('/auth', method='POST',
            body=json_encode(_body))
        self.assertIn('error', response.body.decode('utf-8'))

    def test_authenticated_request(self):
        # create user
        response = self.fetch('/auth', method='PUT',
            body=json_encode(self.body))
        self.assertIn('success', response.body.decode('utf-8'))
        self.assertIn('token', response.body.decode('utf-8'))
        token = json_decode(response.body.decode('utf-8'))['token']

        # use token for authenticated request
        response = self.fetch('/v1/protected', method='GET', headers=HTTPHeaders({
            'Authorization': 'Bearer %s' % token
        }))
        self.assertIn('success', response.body.decode('utf-8'))

        # don't use token for unauthorized request
        response = self.fetch('/v1/protected', method='GET')
        self.assertIn('error', response.body.decode('utf-8'))


class TestMongoDBAuthenticator(testing.AsyncHTTPTestCase, Tests):

    def get_app(self):
        self.body = { "username": "user", "password": "password" }
        self.db = MongoDBMock()

        settings = {
            'secret': 'secret',
            'database': self.db,
        }

        return web.Application([
            (r'/auth', MongoDBAuthenticator),
            (r'/v1/protected', AuthenticatedEndpoint),
        ], **settings)


class TestMemoryAuthenitcator(testing.AsyncHTTPTestCase, Tests):

    def get_app(self):
        self.body = { "username": "user", "password": "password" }

        settings = {
            'secret': 'secret',
            'database': MemoryDB()
        }

        return web.Application([
            (r'/auth', MemoryAuthenticator),
            (r'/v1/protected', AuthenticatedEndpoint),
        ], **settings)
