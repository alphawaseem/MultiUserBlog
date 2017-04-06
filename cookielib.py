"""

This Module helps to encrypt and decrypt cookies using
hmac library

"""

import hmac

# My Secret Key
secret = '$he$lloworld$welcometo$myblog$'

def encrypt_cookie_value(val):
    """
    This Function encrypts the given value using hmac and 
    a secret key
    """
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def decrypt_cookie_value(secure_val):
    """
    This function takes the encrypted value and validates
    it then returns the value
    """
    val = secure_val.split('|')[0]
    if secure_val == encrypt_cookie_value(val):
        return val