auth-backends  |Travis|_ |Codecov|_
===================================
.. |Travis| image:: https://travis-ci.org/edx/auth-backends.svg?branch=master
.. _Travis: https://travis-ci.org/edx/auth-backends

.. |Codecov| image:: http://codecov.io/github/edx/auth-backends/coverage.svg?branch=master
.. _Codecov: http://codecov.io/github/edx/auth-backends?branch=master

This repo houses custom authentication backends, views, and pipeline steps used by edX
projects such as the `edx-analytics-dashboard <https://github.com/edx/edx-analytics-dashboard>`_
and `ecommerce <https://github.com/edx/ecommerce>`_. These components are primarily intended to aid the usage
of edX's single sign-on functionality (built atop OpenID Connect).

This package is compatible with Python 2.7 and 3.5, and Django 1.8 and 1.9.

Installation
------------

The `auth_backends` package can be installed from PyPI using pip::

    $ pip install edx-auth-backends

Backends
--------

Included backends:

===============  ============================================
Backend          Purpose
---------------  --------------------------------------------
Open ID Connect  Authenticate with the LMS, an OIDC provider.
===============  ============================================

Required Django settings:

============================================  ============================================
Setting                                       Default
--------------------------------------------  --------------------------------------------
SOCIAL_AUTH_EDX_OIDC_KEY                      None
SOCIAL_AUTH_EDX_OIDC_SECRET                   None
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY  None
SOCIAL_AUTH_EDX_OIDC_URL_ROOT                 None
EXTRA_SCOPE                                   []
COURSE_PERMISSIONS_CLAIMS                     []
============================================  ============================================

Set these to the correct values for your OAuth2/OpenID Connect provider. ``SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY``
should be the same as ``SOCIAL_AUTH_EDX_OIDC_SECRET``. Set ``EXTRA_SCOPE`` equal to a list of scope strings to request
additional information from the edX OAuth2 provider at the moment of authentication (e.g., provide course permissions bits
to get a full list of courses).

Views
-----

This package includes a login view, ``EdxOpenIdConnectLoginView``, that utilizes edX's implementation of OpenID Connect.
This should be used for all microservices/IDAs.

``LogoutRedirectBaseView`` is also included. It should be overridden, and customized. See the docstring for details.

urls.py
-------

``auth_urlpatterns`` in `urls.py` includes the patterns necessary to facilitate OpenID Connect login. This should
be used by microservices to avoid code duplication. Note that microservices will still need to provide their own
implementations of ``LogoutRedirectBaseView``, and define the linking in the service's `urls.py` file.

Testing
-------

Call ``make test``.

License
-------

The code in this repository is licensed under the AGPL unless otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome!

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though it was written with `edx-platform <https://github.com/edx/edx-platform>`_ in mind,
the guidelines should be followed for Open edX code in general.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Mailing List and IRC Channel
----------------------------

You can discuss this code on the `edx-code Google Group <https://groups.google.com/forum/#!forum/edx-code>`_ or in the
``#edx-code`` IRC channel on Freenode.
