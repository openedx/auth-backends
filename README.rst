auth-backends  |Travis|_ |Coveralls|_
=============
.. |Travis| image:: https://travis-ci.org/edx/auth-backends.svg?branch=master
.. _Travis: https://travis-ci.org/edx/auth-backends

.. |Coveralls| image:: https://img.shields.io/coveralls/edx/auth-backends.svg
.. _Coveralls: https://coveralls.io/r/edx/auth-backends?branch=master

This repo houses custom authentication backends and pipeline steps used by edX
projects such as the `edx-analytics-dashboard <https://github.com/edx/edx-analytics-dashboard>`_
and `edx-ecommerce <https://github.com/edx/edx-ecommerce>`_.

This project is new and under active development.

Overview
--------

Included backends:

===============  ============================================
Backend          Purpose
---------------  --------------------------------------------
Open ID Connect  Authenticate with the LMS, an OIDC provider.
===============  ============================================

This package requires Django 1.7. Required Django settings:

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

Testing
-------

Execute ``test.sh`` to run the test suite.

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

You can discuss this code on the `edx-code Google Group`__ or in the
``#edx-code`` IRC channel on Freenode.

__ https://groups.google.com/forum/#!forum/edx-code
