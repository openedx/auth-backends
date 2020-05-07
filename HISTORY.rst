.. :changelog:

History
=======

3.1.0 (2020-05-08)
------------------
- Added support for python 3.8
- Removed support for Django versions older than 2.2

3.0.2 (2020-02-06)
------------------

Re-release of 3.0.0 with proper version, matching tag.

3.0.1 (2020-02-06)
------------------

Re-release of 3.0.0, although failed to update package version.

3.0.0 (2020-02-06)
------------------

- Add support for Django 2 and drop support for some older versions (support changes from 1.8–1.11 to 1.11–2.2)
- Remove (deprecated) OpenID Connect support
- Test with Python 3.5, not 3.6, to match rest of edX code

2.0.2 (2019-08-12)
------------------

Two new commits that changed functionality:

- Add EdXOAuth2.auth_complete_signal on auth_complete()
- Store refresh_token in extra_data

2.0.1 (2019-05-13)
------------------

Create new Version for auth-backends for release

2.0.0 (2019-03-28)
------------------

EdXOAuth2 will retrieve and store user_id claim

The EdXOAuth2 backend will now pull the user_id from the JWT and
store it in the UserSocialAuth.extra_data field.

BREAKING CHANGE: The user_id scope is now required when using the
EdXOAuth2 backend for oAuth+SSO. This means that the oauth
application must first be configured to have access to the user_id
scope, which is not available by default.

1.2.2 (2019-01-31)
------------------

Updates to the EdXOAuth2 backend:

- Supports the _PUBLIC_URL_ROOT social django setting.
- logout_url() allows _LOGOUT_REDIRECT_URL to be undefined.

1.2.1 (2018-10-26)
------------------

Fix urlencode bug with EdXOAuth2 backend logout url

1.2.0 (2018-10-26)
------------------

Allow for logout redirect with EdXOAuth2 backend.

1.1.5 (2018-10-19)
------------------

Add logout_url property to EdXOAuth2 backend.

1.1.4 (2018-10-12)
------------------

Remove token validation from EdXOAuth2 backend.

1.1.3 (2018-01-04)
------------------

Added support to update email address.

social_core consider email field protected and won't let it change.
Added a pipeline function to update email address.

1.1.2 (2017-05-12)
------------------

Updated LoginRedirectBaseView to include querystring

[unlisted]
----------

Intervening releases not documented here; see Releases:

https://github.com/edx/auth-backends/releases?after=1.1.2


0.1.3 (2015-03-31)
------------------

- Update required version of Python Social Auth to 0.2.3.

0.1.2 (2015-02-23)
------------------

- Update required version of Python Social Auth to 0.2.2.

0.1.1 (2015-02-20)
------------------

- Initial release.
