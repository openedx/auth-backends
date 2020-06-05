0. Purpose of Repo
====================

Status
------

Pending

Decision
--------

The purpose of this repo is to provide a common library for Open edX services
to authenticate against edx-platform and the LMS.


Rationale
---------

We believe that this is important to separate into a separate repo, because we would
like to reduce duplication and repetition of this code across Open edX services.

The tradeoff here is that it will take more time and effort to update and make changes to
the code, and the separate repo may make it more difficult to find this code when doing debugging work.
