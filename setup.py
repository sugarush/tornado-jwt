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
        'pyjwt',
        'tornado',
        'tornado-json==0.0.1'
    ],
    dependency_links=[
        'git+https://github.com/sugarush/tornado-json.git@941d78a6bda7df92f84a534bafac48f759be695b#egg=tornado-json-0.0.1'
    ]
)
