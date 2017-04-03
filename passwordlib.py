import random
from string import letters
import hashlib
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in range(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha512(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def verify_pw_hash(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)