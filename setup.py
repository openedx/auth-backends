from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='edx-auth-backends',
    version='0.1',
    description='Custom edX authentication backends and pipeline steps',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
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
    packages=['auth_backends'],
    install_requires=[
        'Django>=1.7',
        # PSA package on PyPI hasn't been updated to include a fix for a breaking change in PyJWT.
        # For reference on how dependency_links is used here, see http://goo.gl/D5g4Qq.
        'python-social-auth<=0.2.2'
    ],
    dependency_links=[
        'git+https://github.com/omab/python-social-auth.git@bdf69d67d109acfda1016d4a2a63a1cc0a3aba84#egg=python-social-auth-0.2.2',
    ]
)
