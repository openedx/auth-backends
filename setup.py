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
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Topic :: Internet',
    ],
    keywords='authentication edx',
    url='https://github.com/edx/auth-backends',
    author='edX',
    author_email='oscm@edx.org',
    license='AGPL',
    packages=find_packages(),
    install_requires=[
        'Django>=1.8,<1.10',
        # 0.3.0 introduced a major breaking change, effectively gutting PSA and
        # moving its Django components to a new social-auth-app-django package.
        # We may require the new package at some point in the future, once it's stable.
        'python-social-auth>=0.2.21,<0.3.0',
        'six>=1.10.0,<2.0.0'
    ],
)
