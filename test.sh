#!/bin/sh

python manage.py test auth_backends --with-coverage --cover-package=auth_backends
