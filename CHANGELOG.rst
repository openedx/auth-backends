Change Log
==========

..
   This file loosely adheres to the structure of https://keepachangelog.com/,
   but in reStructuredText instead of Markdown.

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
----------


[4.6.1] - 2025-07-25
--------------------

Added
~~~~~

* Added IGNORE_LOGGED_IN_USER_ON_MISMATCH toggle to handle username mismatches in authentication pipeline.
* Enhanced get_user_if_exists function with monitoring capabilities for debugging authentication conflicts.

Fixed
~~~~~

* Fixed authentication issues where username mismatches between logged-in users and social auth details caused "user already exists" errors.
* Improved user account conflict resolution in devstack and stage environments.

[4.6.0] - 2025-06-18
--------------------

Changed
~~~~~~~

* Improved test coverage by replacing MagicMock with real load_strategy() implementation.
* Fixed email update handling in authentication pipeline.
* Added logging for email updates.

Added
~~~~~~~

[4.5.0] - 2025-04-09
--------------------

* Added support for Django 5.2

[4.4.0] - 2024-09-10
--------------------

* Dropped support for python3.8

[4.3.0] - 2024-04-01
--------------------

* Added support for python3.11 and 3.12
* Dropped django 3.2 support.

[4.2.0] - 2023-08-03
--------------------

* Added support for Django 4.2

[4.1.0] - 2022-01-28
--------------------

Removed
~~~~~~~

* Removed Django22, 30, 31

Added
~~~~~~~
* Added Django40 support in CI


[4.0.1] - 2021-11-01
--------------------

Changed
~~~~~~~

* Resolve RemovedInDjango4.0 warnings.


[4.0.0] - 2021-08-05
--------------------

Changed
~~~~~~~

* **BREAKING CHANGE:** ``jwt.decode``: Inside ``EdXOAuth2::user_data`` Require explicit algorithms by default.
* **BREAKING CHANGE:** Upgraded dependency ``pyjwt[crypto]`` to 2.1.0, which introduces its own breaking changes that may affect consumers of this library. Pay careful attention to the 2.0.0 breaking changes documented in https://pyjwt.readthedocs.io/en/stable/changelog.html#v2-0-0.


[3.4.0] - 2021-07-07
--------------------

Added
~~~~~~~

* Added support for django 3.1 and 3.2

[3.3.3] - 2021-02-02
--------------------

Changed
~~~~~~~

* Fixed the changelog to match the package version

[3.1.0] - 2020-05-08
--------------------

Added
~~~~~

* Add python 3.8 support

Removed
~~~~~~~

* Removed Django <2.2

[3.0.2] - 2020-02-06
--------------------

No functional changes. Fixed release version.

[3.0.1] - 2020-02-06
--------------------

No functional changes. 3.0.0 had failed to release.

[3.0.0] - 2020-02-06
--------------------

Removed
~~~~~~~

* **BREAKING CHANGE**: Remove (deprecated) OpenID Connect support
* **BREAKING CHANGE**: Remove Django <1.11 support
* Remove testing of Python 3.6

Added
~~~~~

* Add support for Django 2.2
* Add testing of Python 3.5
