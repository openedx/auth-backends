""" Django authentication backends.

 These package is designed to be used primarily with Open edX Django projects, but should be compatible with non-edX
 projects as well.
"""
from importlib.metadata import version

__version__ = version("edx-auth-backends")
