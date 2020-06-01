Change Log
==========

..
   This file loosely adheres to the structure of https://keepachangelog.com/,
   but in reStructuredText instead of Markdown.

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
----------

* Added a decisions directory for recording any architectural changes made to this repo.


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
