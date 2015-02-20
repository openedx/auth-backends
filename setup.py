#!/usr/bin/env python

from setuptools import setup, find_packages

from auth_backends._version import __version__


with open('README.rst') as a, open('HISTORY.rst') as b, open('AUTHORS') as c:
    long_description = '{}\n\n{}\n\n{}'.format(a.read(), b.read(), c.read())

setup(
    name='edx-auth-backends',
    version=__version__,
    description='Custom edX authentication backends and pipeline steps',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
    ],
    keywords='authentication edx',
    url='https://github.com/edx/auth-backends',
    author='edX',
    author_email='oscm@edx.org',
    license='AGPL',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'Django>=1.7',
    ],
)
