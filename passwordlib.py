"""
This module helps to hash passwords with random salts
"""

# Import neccessary modules
import random
from string import letters
import hashlib


def make_salt(length=5):
    """
    returns a random salt of default length of 5
    """
    return ''.join(random.choice(letters) for x in range(length))


def make_pw_hash(name, pw, salt=None):
    """
    returns a salt and hashed value  in the format %s,%salt
    If salt in not given then it creates a new salt and returns
    hashed value with salt. Else use that salt to generate hash this 
    is useful when verifying the hash with raw values. 
    It uses sha512 and mix of name password and salt.
    """
    if not salt:
        salt = make_salt()
    h = hashlib.sha512(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def verify_pw_hash(name, password, h):
    """
    returns True/False if name and password generates same given hash
    which contains salt. We use this salt value to regenerate the hash
    and match it with given hash.
    """
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)