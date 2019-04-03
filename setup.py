#!/usr/bin/env python

from setuptools import setup, find_packages

from auth_backends import __version__

with open('README.rst') as a, open('HISTORY.rst') as b, open('AUTHORS') as c:
    long_description = '{}\n\n{}\n\n{}'.format(a.read(), b.read(), c.read())

setup(
    name='edx-auth-backends',
    version=__version__,
    description='Custom edX authentication backends and pipeline steps',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Topic :: Internet',
    ],
    keywords='authentication edx',
    url='https://github.com/edx/auth-backends',
    author='edX',
    author_email='oscm@edx.org',
    license='AGPL',
    packages=find_packages(),
    install_requires=[
        'Django>=1.11,<2.3',
        'pyjwt',
        'six',
        'social-auth-core[openidconnect]>=3.1.0,<4.0.0',
        'social-auth-app-django>=3.1.0,<4.0.0',
    ],
)
