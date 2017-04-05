auth-backends  |Travis|_ |Codecov|_
===================================
.. |Travis| image:: https://travis-ci.org/edx/auth-backends.svg?branch=master
.. _Travis: https://travis-ci.org/edx/auth-backends

.. |Codecov| image:: http://codecov.io/github/edx/auth-backends/coverage.svg?branch=master
.. _Codecov: http://codecov.io/github/edx/auth-backends?branch=master

This repo houses a custom authentication backend, views, and pipeline steps used by edX services for single sign-on.
This functionality is built atop the `OpenID Connect (OIDC) protocol <http://openid.net/connect/>`_.

This package is compatible with Python 2.7 and 3.5, and Django 1.8 through 1.11.

Installation
------------

The `auth_backends` package can be installed from PyPI using pip::

    $ pip install edx-auth-backends

Configuration
-------------
Adding single sign-on/out support to a service requires a few changes:

1. Define settings
2. Add the authentication backend
3. Add the login/logout redirects


Settings
~~~~~~~~
The following settings MUST be set:

+----------------------------------------------+---------------------------------------------------------------------------------------------+
| Setting                                      | Purpose                                                                                     |
+==============================================+=============================================================================================+
| SOCIAL_AUTH_EDX_OIDC_KEY                     | OAuth/OpenID Connect client key                                                             |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OIDC_SECRET                  | OAuth/OpenID Connect client secret                                                          |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY | Identity token decryption key (same value as the client secret for edX OpenID Connect)      |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OIDC_URL_ROOT                | OAuth/OpenID Connect provider root (e.g. https://courses.stage.edx.org/oauth2)              |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_EDX_OIDC_LOGOUT_URL              | OAuth/OpenID Connect provider's logout page URL (e.g. https://courses.stage.edx.org/logout) |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| SOCIAL_AUTH_STRATEGY                         | Python Social Auth strategy. Set this to `'auth_backends.strategies.EdxDjangoStrategy'`     |
+----------------------------------------------+---------------------------------------------------------------------------------------------+

If your application requires additional user data in the identity token, you can specify additional claims by defining
the ``EXTRA_SCOPE`` setting. For example, if you wish to have a claim named `preferred_language`, you would include
the following in your settings:

.. code-block:: python

    EXTRA_SCOPE = ['preferred_language']

Assuming the identity provider knows how to process that scope, the associated claim data will be included in the
identity token returned during authentication. Note that these scopes/claims are dependent on the identity provider
being used. The ``EdXOpenIdConnect`` backend is configured to be used by all edX services out-of-the-box.

The optional setting ``COURSE_PERMISSIONS_CLAIMS``, used primarily by
`edx-analytics-dashboard <https://github.com/edx/edx-analytics-dashboard>`_, can be used to designate scopes/claims that
should be requested in order to retrieve a list of courses the user is permitted to access/administer. The value of this
array depends on the authentication provider's available scopes.

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
        'auth_backends.backends.EdXOpenIdConnect',
        'django.contrib.auth.backends.ModelBackend',
    )

Authentication Views
~~~~~~~~~~~~~~~~~~~~
In order to make use of the authentication backend, your service's login/logout views need to be updated. The login
view should be updated to redirect to the OpenID Connect provider's login page. The logout view should be updated to
redirect to the OpenID Connect provider's logout page.

This package includes views and urlpatterns configured for edX OpenID Connect. To use them, simply append/prepend
``auth_urlpatterns`` to your service's urlpatterns in `urls.py`.

.. code-block:: python

    from auth_backends.urls import auth_urlpatterns

    urlpatterns = auth_urlpatterns + [
        url(r'^admin/', include(admin.site.urls)),
        ...
    ]

It is recommended that you not modify the login view. If, however, you need to modify the logout view (to redirect to
a different URL, for example), you can subclass ``EdxOpenIdConnectLogoutView`` for the view and ``LogoutViewTestMixin``
for your tests.

Devstack
--------
When using the Docker-based devstack, it is necessary to have both internal and public URLs for the OAuth/OIDC
provider. To accommodate this need, set the ``SOCIAL_AUTH_EDX_OIDC_PUBLIC_URL_ROOT`` setting to the value of the
provider's browser-accessible URL.

.. code-block:: python

    SOCIAL_AUTH_EDX_OIDC_URL_ROOT = 'http://edx.devstack.edxapp:18000/oauth2'
    SOCIAL_AUTH_EDX_OIDC_PUBLIC_URL_ROOT = 'http://localhost:18000/oauth2'

Additionally, the logout URL should also be browser-accessible:

.. code-block:: python

    SOCIAL_AUTH_EDX_OIDC_LOGOUT_URL = 'http://localhost:18000/logout'

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
