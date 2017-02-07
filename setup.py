__author__ = 'napalmbrain'

from setuptools import setup

setup(
    name='tornado-jwt',
    version='0.0.1',
    author='napalmbrain',
    author_email='github@napalmbrain.sugarush.io',
    url='https://github.com/sugarush/tornado-jwt',
    packages=['tornado_jwt'],
    description='An asynchronous JWT authentication module for Tornado.',
    install_requires=[
        'tornado',
        'tornado-json==0.0.1'
    ],
    dependency_links=[
        'git+https://github.com/sugarush/tornado-json.git@93adcf9e29e3f99c44d93d71292df63ceb5b7df7#egg=tornado-json-0.0.1'
    ]
)
