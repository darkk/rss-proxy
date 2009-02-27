# -*- encoding: utf-8 -*-

from base64 import b64encode, b64decode
from urllib import urlencode

from django.conf import settings
from django.http import QueryDict

from p3 import p3_encrypt, p3_decrypt, CryptError

B64_ALTCHARS = '-_'

def encrypt(d):
    """ encrypts dictionary to url-safe string """
    return b64encode(p3_encrypt(urlencode(d), settings.SECRET_KEY), B64_ALTCHARS)

def decrypt(code):
    """ decrypts url-safe string to dictinoary """
    return QueryDict(p3_decrypt(b64decode(str(code), B64_ALTCHARS), settings.SECRET_KEY))
