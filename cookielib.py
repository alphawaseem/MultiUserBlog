

import hmac

secret = '$he$lloworld$welcometo$myblog$'

def encrypt_cookie_value(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def decrypt_cookie_value(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == encrypt_cookie_value(val):
        return val