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
        'git+https://github.com/sugarush/tornado-json.git@d881e94129056e9e27d188d0d189f52104f139b6#egg=tornado-json-0.0.1'
    ]
)
