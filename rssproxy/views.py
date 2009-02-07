# -*- coding: utf-8 -*-

import logging
import re
from urllib import urlencode
import urllib2
import httplib
from base64 import b64encode, b64decode
from crypt import crypt
import xml.etree.ElementTree as ElementTree
from random import getrandbits
from array import array

import google.appengine.api.urlfetch_errors as urlfetch_errors
import google.appengine.runtime as GAEruntime

from django.conf import settings
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.cache import cache

from p3 import p3_encrypt, p3_decrypt, CryptError

import lj

def _urlopen_digested(url, username, pw, headers = {}):
    pwmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # None is the default realm
    pwmgr.add_password(None, url, username, pw)
    authhandler = urllib2.HTTPDigestAuthHandler(pwmgr)
    opener = urllib2.build_opener(authhandler)
    return opener.open(urllib2.Request(url=url, headers=headers))


B64_ALTCHARS = '-_'

BLOCKED_REQEST_HEADERS = (
    # from http://code.google.com/appengine/docs/urlfetch/fetchfunction.html
    'content-length',
    'host',
    'referer',
    'user-agent',
    'vary',
    'via',
    'x-forwarded-for',
    # extras from http://code.google.com/p/googleappengine/issues/detail?id=342
    'date',
    'accept-encoding',
    # extras from darkk
    'keep-alive',
    'connection')

BLOCKED_RESPONSE_HEADERS = (
    # from http://code.google.com/p/googleappengine/issues/detail?id=342
    'content-encoding',
    'content-length',
    'date',
    'server',
    'transfer-encoding')

def lj_dispatcher(req):
    if req.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])

    action_map = {'login': _lj_check_login,
                  'opml':  _lj_gen_opml}
    def default(req):
        return render_to_response('lj_login.html')

    action = action_map.get(req.POST.get('action'), default)
    return action(req)

class LjLoginCheckState:
    # it MAY be bad idea to build brute-force protection on top of
    # memcache, but I assume it's good enough for me.
    def __init__(self, ljuser):
        self.ljuser = ljuser
        self.cacheaddr = 'ljpasswd:' + ljuser

        state = cache.get(self.cacheaddr)
        if state:
            self.attempts = state.attempts
            self.pass_is_ok = state.pass_is_ok
            self.crypted = state.crypted
        else:
            self.attempts = 0
            self.pass_is_ok = None
            self.crypted = None

    def make_attempt(self, password):
        """
        Returns one of the following httplib codes:
        OK           — password matches
        FORBIDDEN    — if user can't make attempts
        NOT_FOUND    - if user is not found
        UNAUTHORIZED - if password does not match
        BAD_GATEWAY  - if network error occures
        """
        if self._same_password(password) and self.pass_is_ok is not None:
            return self.pass_is_ok

        self.attempts += 1
        if self.attempts > 5:
            return httplib.FORBIDDEN

        salt = b64encode(array('H', [getrandbits(16)]).tostring(), altchars='./')[0:2]
        self.crypted = crypt(password, salt)
        self.pass_is_ok = self._make_attempt(password)
        cache.add(self.cacheaddr, self, 60)
        return self.pass_is_ok

    def _same_password(self, password):
        return self.crypted is not None and crypt(password, self.crypted) == self.crypted

    def _make_attempt(self, password):
        """ Inernal network part without any extra logic. """
        try:
            _urlopen_digested(
                    lj.baseurl(self.ljuser) + '/data/rss?auth=digest',
                    self.ljuser, password)
            return httplib.OK
        except urllib2.HTTPError, e:
            if e.code in (httplib.NOT_FOUND, httplib.GONE):
                return httplib.NOT_FOUND
            if e.code == httplib.UNAUTHORIZED:
                return httplib.UNAUTHORIZED
            logging.warning("Network error", exc_info=1)
            return httplib.BAD_GATEWAY
        except (urlfetch_errors.DownloadError,
                GAEruntime.DeadlineExceededError,
                IOError):
            logging.warning("Network error", exc_info=1)
            return httplib.BAD_GATEWAY


def _lj_check_login(req):
    ljuser = req.POST.get('ljuser', '').strip()
    password = req.POST.get('password', '')

    def mkret(ctx):
        return render_to_response('lj_login.html',
                dict([('ljuser', ljuser)] + ctx.items()))

    if not lj.is_valid_login(ljuser):
        return mkret({'bad_ljuser': True})

    if not lj.is_valid_password(password):
        return mkret({'bad_password': True})

    state = LjLoginCheckState(ljuser)
    reply = state.make_attempt(password)
    if reply == httplib.OK:
        return _lj_mkpage_gen_opml(ljuser, password)
    action_map = {httplib.FORBIDDEN: 'bad_guy',
                  httplib.NOT_FOUND: 'bad_ljuser',
                  httplib.UNAUTHORIZED: 'bad_password',
                  httplib.BAD_GATEWAY:  'bad_gateway'}
    return mkret({action_map.get(reply, 'bad_gateway'): True})

def _lj_mkpage_gen_opml(ljuser, password):
    fset = lj.get_fdata(ljuser)
    include_myself = bool(ljuser in fset['friends'])
    outlines = lj.get_opml(ljuser)

    ctx = {'credentials': _encrypt({'ljuser': ljuser, 'password': password})}

    def mkfriend_ctx(f):
        return {'login': f,
                'url': outlines['users'][f].htmlURL,
                'journal_name': outlines['users'][f].text}

    mutual_friends = fset['friends'].intersection(fset['fans'])
    ctx['mutual_friends'] = [mkfriend_ctx(f) for f in mutual_friends]

    friends_of = fset['friends'].difference(fset['fans'])
    ctx['friends_of'] = [mkfriend_ctx(f) for f in friends_of]

    ctx['communities'] = []
    for o in outlines['communities'].itervalues():
        ctx['communities'].append({'url': o.htmlURL,
                                   'login': o.login,
                                   'journal_name': o.text})

    return render_to_response('lj_mkopml.html', ctx)


def _lj_gen_opml(req):
    credentials = _decrypt(req.POST['credentials'])
    friends = req.POST['friends'].split()
    communities = req.POST['communities'].split()

    ljuser = credentials['ljuser']
    password = credentials['password']

    outlines = lj.get_opml(ljuser)
    outlines['users'].update(outlines['communities'])
    outlines = outlines['users']

    ctx = {'ljuser': ljuser}
    feeds = []
    for who in friends + communities:
        o = outlines[who]
        if req.POST.get('read_' + who):
            param = {'feed': o.xmlURL + '?auth=digest',
                     'user': ljuser,
                     'password': password}
            if req.POST.get('cut_' + who):
                param['ljcut'] = 'body'
            xmlURL = req.build_absolute_uri('/feed/' + _encrypt(param))
        else:
            xmlURL = outlines[who].xmlURL

        if o.text.lower() != who.lower():
            text = "%s (%s)" % (o.text, who)
        else:
            text = o.text

        feeds.append({'xmlURL':  xmlURL,
                      'htmlURL': o.htmlURL,
                      'text':    text})
    ctx['feeds'] = feeds
    content = render_to_string('lj_opml.xml', ctx)
    resp = HttpResponse(content_type='text/xml', content=content)
    resp['Content-Disposition'] = 'attachment; filename="livejournal.opml"'
    return resp



def _encrypt(d):
    """ encrypts dictionary """
    return b64encode(p3_encrypt(urlencode(d), settings.SECRET_KEY), B64_ALTCHARS)

def _decrypt(code):
    """ decrypts string """
    return QueryDict(p3_decrypt(b64decode(str(code), B64_ALTCHARS), settings.SECRET_KEY))


def lj_opml_get(req):
    # FIXME: this is legacy interface, remove it after one month of inactivity
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
            feed = _encrypt({'feed': url, 'user': user, 'password': password})
            el.set('xmlURL', req.build_absolute_uri('/feed/' + feed))

    return HttpResponse(
            content_type='application/xml',
            content=ElementTree.tostring(tree.getroot()))


def generic_mkfeed(req):
    if req.method == 'GET':
        return render_to_response('generic.html')
    elif req.method == 'POST':
        # FIXME: rewrite using django forms & proper validation
        param = {'feed':     req.POST.get('feed'),
                 'user':     req.POST.get('feed'),
                 'password': req.POST.get('feed')}
        feed = _encrypt(param)
        return HttpResponseRedirect(req.build_absolute_uri('/feed/' + feed))
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def _ljcut_nonpublic(content, feed=None, user=None):
    # LiveJournal can produce RSS-feed that is not UTF-8/strict if user
    # sent some garbage to it. Garbage-in-garbage-out :-)
    recoded = content.decode('utf-8', 'replace').encode('utf-8')
    if recoded != content:
        logging.warning('Invalid utf-8 data while fetching feed <%s> for %s' % (feed, user))

    chunk = ElementTree.XML(recoded)
    for item in chunk.findall('.//item'):
        NS = 'http://www.livejournal.org/rss/lj/1.0/'
        nonpublic = sum(1 for s in item.findall('./{%s}security' % NS) if s.text !='public')
        if nonpublic:
            for description in item.findall('./description'):
                description.text = u'It\'s a non-public record. © rss-proxy'
    return "<?xml version='1.0' encoding='utf-8' ?>" + ElementTree.tostring(chunk, 'utf-8')

def get_feed(req, code):
    if req.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    try:
        q = _decrypt(code)
        feed = q['feed']
        user = q['user']
        password = q['password']
        ljcut = True if q.get('ljcut') else False
    except (TypeError, CryptError, KeyError):
        # TypeError on b64decode failure
        return HttpResponseBadRequest()

    headers = {}
    for header, value in req.META.items():
        if header.startswith('HTTP_'):
            header = header.replace('_', '-').split('-', 1)[1]
            if header.lower() not in BLOCKED_REQEST_HEADERS:
                headers[header.title()] = value

    try:
        fd = _urlopen_digested(feed, user, password, headers)
        headers = fd.headers
        content = fd.read()
        if ljcut:
            content = _ljcut_nonpublic(content, feed, user)
    except urllib2.HTTPError, e:
        # FIXME: what should happen if remote side returns permanent redirect?
        if e.code >= 400:
            logging.warning('HTTPError %i while fetching feed <%s> for %s' %
                            (e.code, feed, user))
        fd = e
        headers = fd.hdrs
        content = fd.read() if hasattr(fd, 'read') else ''
    except urlfetch_errors.DownloadError, e:
        # FIXME: check for URLFetchServiceError.DEADLINE_EXCEEDED and
        #        return 504 (httplib.GATEWAY_TIMEOUT)
        return HttpResponseServerError(
                status=httplib.BAD_GATEWAY,
                content_type='text/plain',
                content='Feed can\'t be fetched: ' + str(e))
    except GAEruntime.DeadlineExceededError:
        # There is bug in GAE-SDK-1.1.7 — DeadlineExceededError is not
        # converted to DownloadError (it should be, according to code).
        # Let's benefit from the bug :-)
        # http://code.google.com/p/googleappengine/issues/detail?id=973
        return HttpResponseServerError(
                status=httplib.GATEWAY_TIMEOUT,
                content_type='text/plain',
                content='Feed can\'t be fetched: timeout.')


    resp = HttpResponse(content=content, status=fd.code)
    for header, value in headers.items():
        if not header in BLOCKED_RESPONSE_HEADERS + ('www-authenticate', ):
            resp[header] = value
    return resp
