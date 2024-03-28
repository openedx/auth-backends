Change Log
==========

..
   This file loosely adheres to the structure of https://keepachangelog.com/,
   but in reStructuredText instead of Markdown.

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
----------

*

Added
~~~~~~~

[4.3.0] - 2024-02-13
--------------------

* Added support for python3.11. Dropped django3.2 support.

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
