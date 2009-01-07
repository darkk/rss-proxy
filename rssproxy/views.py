# -*- coding: utf-8 -*-
from urllib import urlencode
import urllib2
import httplib
from base64 import b64encode, b64decode
import xml.etree.ElementTree as ElementTree

import google.appengine.api.urlfetch_errors as urlfetch_errors

from django.conf import settings
from django.http import QueryDict, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseServerError

from p3 import p3_encrypt, p3_decrypt

def _urlopen_digested(url, username, pw):
    pwmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # None is the default realm
    pwmgr.add_password(None, url, username, pw)
    authhandler = urllib2.HTTPDigestAuthHandler(pwmgr)
    opener = urllib2.build_opener(authhandler)
    return opener.open(url)

B64_ALTCHARS = '-_'

BLOCKED_HEADERS = set((
    'content-length',
    'host',
    'referer',
    'user-agent',
    'vary',
    'via',
    'x-forwarded-for',
    ))

def lj_opml_get(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = req.POST.get('user', '').replace('-', '_')
    password = req.POST.get('password', '')

    if not user or not password:
        return HttpResponseBadRequest(
                            content_type='text/plain',
                            content='`user` or `password` is missing.')

    fd = urllib2.urlopen('http://www.livejournal.com/tools/opml.bml?' + urlencode({'user': user}))
    tree = ElementTree.parse(fd)
    for el in tree.findall('//outline'):
        url = el.get('xmlURL', None)
        if url is not None:
            url += '?auth=digest'
            feed = b64encode(
                    p3_encrypt(
                        urlencode({'feed': url, 'user': user, 'password': password}),
                        settings.SECRET_KEY),
                    B64_ALTCHARS)
            el.set('xmlURL', req.build_absolute_uri('/feed/' + feed))

    return HttpResponse(
            content_type='application/xml',
            content=ElementTree.tostring(tree.getroot()))


def get_feed(req, code):
    q = QueryDict(p3_decrypt(b64decode(code.encode('ascii'), B64_ALTCHARS), settings.SECRET_KEY))
    feed = q.get('feed')
    user = q.get('user')
    password = q.get('password')
    if not feed or not user or not password:
        return HttpResponseBadRequest()

    try:
        fd = _urlopen_digested(feed, user, password)
    except urllib2.HTTPError, e:
        # FIXME: urllib2.HTTPError MAY contain NO .read() if it has not
        #        associated file descriptor e.g. in case of failed
        #        digest authentication
        fd = e
    except urlfetch_errors.DownloadError, e:
        # FIXME: check for URLFetchServiceError.DEADLINE_EXCEEDED and
        #        return 504 (httplib.GATEWAY_TIMEOUT)
        return HttpResponseServerError(
                status=httplib.BAD_GATEWAY,
                content_type='text/plain',
                content='Feed can\'t be fetched: ' + str(e))

    content = fd.read()
    resp = HttpResponse(content=content, status=fd.code)
    for header, value in fd.headers.items():
        if not header in BLOCKED_HEADERS:
            resp[header] = value
    return resp
