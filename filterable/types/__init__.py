from .json import JSONB
from .array import ARRAY

"""
These custom types prevents failing tests when your are using JSONB or ARRAY on
SQLite, once it doesn't give support for these types (JSONB and ARRAY). 

As a workaround, these "custom types" try to load the native type, and return a 
simple JSON if it gets an ImportError, to prevent incompatibility type error 
between your Test and App environment.
"""

JSONB = JSONB
ARRAY = ARRAY