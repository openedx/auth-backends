import os

from setuptools import setup, find_packages


exec(open('auth_backends/_version.py').read())


def read(*paths):
    """Build a file path from `paths` and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='edx-auth-backends',
    version=__version__,
    description='Custom edX authentication backends and pipeline steps',
    long_description=(
        read('README.rst') + '\n\n' +
        read('HISTORY.rst') + '\n\n' +
        read('AUTHORS')
    ),
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
