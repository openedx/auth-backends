auth-backends  |CI|_ |Codecov|_
===================================
.. |CI| image:: https://github.com/edx/auth-backends/workflows/Python%20CI/badge.svg?branch=master
.. _CI: https://github.com/edx/auth-backends/actions?query=workflow%3A%22Python+CI%22

.. |Codecov| image:: http://codecov.io/github/edx/auth-backends/coverage.svg?branch=master
.. _Codecov: http://codecov.io/github/edx/auth-backends?branch=master

This package contains custom authentication backends, views, and pipeline steps used by edX services for single sign-on.

This package is compatible with Python 3.8, Django 2.2 and Django 3.0

We currently support OAuth 2.0 authentication. Support for OpenID Connect (OIDC) was removed as of version 3.0. Use version 2.x if you require OIDC and are not able to migrate to OAuth2.

Installation
------------

The `auth_backends` package can be installed from PyPI using pip::

    $ pip install edx-auth-backends

Update ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        'social_django',
    )


Configuration
-------------
Adding single sign-on/out support to a service requires a few changes:

1. Define settings
2. Add the authentication backend
3. Add the login/logout redirects


OAuth 2.0 Settings
~~~~~~~~~~~~~~~~~~
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| Setting                                                  | Purpose                                                                                   |
+==========================================================+===========================================================================================+
| SOCIAL_AUTH_EDX_OAUTH2_KEY                               | Client key                                                                                |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OAUTH2_SECRET                            | Client secret                                                                             |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT                          | LMS root, reachable from the application server                                           |
|                                                          | (e.g. https://courses.stage.edx.org or http://edx.devstack.lms:18000)                     |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT                   | LMS root, reachable from the end user's browser                                           |
|                                                          | (e.g. https://courses.stage.edx.org or http://localhost:18000)                            |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OAUTH2_JWS_HMAC_SIGNING_KEY              | (Optional) Shared secret for JWT signed with HS512 algorithm                              |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OAUTH2_PROVIDER_CONFIGURATION_CACHE_TTL  | (Optional) Cache timeout for provider configuration. Defaults to 1 week.                  |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OAUTH2_JWKS_CACHE_TTL                    | (Optional) Cache timeout for provider's JWKS key data. Defaults to 1 day.                 |
+----------------------------------------------------------+-------------------------------------------------------------------------------------------+

OAuth2 Applications require access to the ``user_id`` scope in order for the ``EdXOAuth2`` backend to work.  The backend will write the ``user_id`` into the social-auth extra_data, and can be accessed within the User model as follows::

    self.social_auth.first().extra_data[u'user_id']  # pylint: disable=no-member

Strategy
~~~~~~~~
We use a custom `strategy <http://python-social-auth.readthedocs.io/en/latest/strategies.html>`_ that includes many of
the default settings necessary to utilize single sign-on for edX services. This strategy should be used for all
services to simplify configuration. If you need to override the defaults, you may still do so as you would with any
social auth setting——prepend `SOCIAL_AUTH_` to the setting name. Add the following to your Django settings to use the
strategy:

.. code-block:: python

    SOCIAL_AUTH_STRATEGY = 'auth_backends.strategies.EdxDjangoStrategy'

Authentication Backend
~~~~~~~~~~~~~~~~~~~~~~
Configuring the backend is simply a matter of updating the ``AUTHENTICATION_BACKENDS`` setting. The configuration
below is sufficient for all edX services.

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'auth_backends.backends.EdXOAuth2',
        'django.contrib.auth.backends.ModelBackend',
    )

Authentication Views
~~~~~~~~~~~~~~~~~~~~
In order to make use of the authentication backend, your service's login/logout views need to be updated. The login
view should be updated to redirect to the authentication provider's login page. The logout view should be updated to
redirect to the authentication provider's logout page.

This package includes views and urlpatterns configured for OAuth 2.0. To use them, simply append/prepend
``oauth2_urlpatterns`` to your service's urlpatterns in `urls.py`.

.. code-block:: python

    from auth_backends.urls import oauth2_urlpatterns

    urlpatterns = oauth2_urlpatterns + [
        url(r'^admin/', include(admin.site.urls)),
        ...
    ]

It is recommended that you not modify the login view. If, however, you need to modify the logout view (to redirect to
a different URL, for example), you can subclass ``EdxOAuth2LogoutView`` for
the view and ``LogoutViewTestMixin`` for your tests.

Testing
-------

Call ``make test``.

Publishing a Release
--------------------

After a PR merges, create a new tag from ``master`` branch with a new version of the package and create a
`Github release <https://github.com/edx/auth-backends/releases>`_
using the new tag that will automatically publish the package to PyPi when a release is created.


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
