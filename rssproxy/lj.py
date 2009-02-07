# -*- encoding: utf-8 -*-
# Livejournal toolkit, includes some simple caching.

import re
import urllib2
from urllib import urlencode, addinfourl
import httplib
import logging
from StringIO import StringIO
import xml.etree.ElementTree as ElementTree

from django.core.cache import cache


# LiveJournal does not support Last-Modified/If-Modified-Since validators.
# It also does not provide any timeouts with Cache-Control/Expires.
# But some pages support Etag/If-None-Match so I implement it and only it.
# By the way, FOAF (the heaviest page) does not support Etag on 01 Feb 2009

class CachedPage:
    def __init__(self, url, headers, data):
        self.url = url
        self.headers = headers
        self.data = data

    def mkaddinfourl(self):
        return addinfourl(StringIO(self.data), self.headers, self.url)


def cached_urlopen(req, *args, **kwargs):
    PREFIX = 'webcache:'

    if isinstance(req, basestring):
        url = req
        req = urllib2.Request(url)
    else:
        assert req.get_method() == 'GET'
        url = req.get_full_url()

    cacheaddr = PREFIX + url
    page = cache.get(cacheaddr)

    if not page or page.headers.get('ETag'):
        if page and page.headers.get('ETag'):
            req.add_header('If-None-Match', page.headers.get('ETag'))
        try:
            # FIXME: this should be rather done with urllib2 opener, but
            #        I don't want to dive into openers right now, see
            #        <http://diveintopython.org/http_web_services/etags.html>
            #        if you want to.
            fd = urllib2.urlopen(req, *args, **kwargs)
            # we're here if page was either modified or not cached
            timeout = 15*60 if fd.headers.get('ETag') else 3*60
            page = CachedPage(url, dict(fd.headers.items()), fd.read())
            cache.set(cacheaddr, page, timeout)
            return page.mkaddinfourl()
        except urllib2.HTTPError, e:
            if e.code == httplib.NOT_MODIFIED:
                # Should cache be refreshed? I don't know. Let it be so.
                cache.set(cacheaddr, page, 15*60)
                return page.mkaddinfourl()
            else:
                raise
    else:
        return page.mkaddinfourl()


def get_fdata(user):
    """ Returns dict{'friends": set(...), 'fans': set(...)}"""
    fd = cached_urlopen('http://www.livejournal.com/misc/fdata.bml?' + urlencode({'user': user}))
    return parse_fdata(fd, user)

def parse_fdata(fd, user=None):
    friends = set()
    fans = set()

    for line in fd:
        line = line.rstrip()
        if line.startswith('#'):
            pass
        elif line.startswith('> '):
            friends.add(line[2:])
        elif line.startswith('< '):
            fans.add(line[2:])
        elif line:
            logging.warning('LJ: unknown line in <%s>\'s fdata: <%s>' % (user, line))
    return {'friends': friends, 'fans': fans}


def baseurl(user):
    return 'http://%s.livejournal.com' % dnsize(user)

def baseurl_comm(comm):
    return 'http://community.livejournal.com/%s' % comm

def dnsize(user):
    """ Convert LJ username to DNS-friendly form """
    return user.replace('_', '-')


class LJUser:
    def __init__(self, nick, member_name, tagLine, image=None):
        self.login = nick
        self.name = member_name
        self.journal_name = tagLine
        self.avatar = image

    @property
    def url(self):
        return baseurl(self.login)


def get_foaf(user, include_myself=False):
    """
    Returns list of friends of `user' as a dict.
    Keys are usernames, values are `LJUser' instances.
    """
    assert user.replace('_', '').isalnum()

    url = baseurl(user) + '/data/foaf'
    fd = cached_urlopen(url)
    return parse_foaf(fd, include_myself)

def parse_foaf(fd, include_myself=False):
    """
    Parses LJ Friend-Of-A-Friend file.

    You should not rely on it's information: sometimes it's empty when
    user has ~100 friends, sometimes it's limited to ~970 items when
    user has ~1500..2000 friends.
    """
    ns = {'foaf': '{http://xmlns.com/foaf/0.1/}',
          'rdf':  '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'}
    retval = {}
    tree = ElementTree.parse(fd)
    for el in tree.findall('/%(foaf)sPerson/%(foaf)sknows/%(foaf)sPerson' % ns):
        kwargs = {}
        for tag in ('nick', 'member_name', 'tagLine', 'image'):
            kwargs[tag] = el.findtext('%s%s' % (ns['foaf'], tag))
        retval[kwargs['nick']] = LJUser(**kwargs)

    if include_myself:
        el = tree.find('/%(foaf)sPerson' % ns)
        kwargs = {'nick':        el.findtext('%(foaf)snick' % ns),
                  'member_name': el.findtext('%(foaf)sname' % ns),
                  'tagLine':     u'N/A (собственный блог)'}
        image = el.find('%(foaf)simg' % ns)
        if image is not None:
            # XXX: maybe, Python 2.5 bug, '{rdf}:resource' does not work
            #      but it is expeted to work as far as I see
            kwargs['image'] = image.get('%(rdf)sresource' % ns)
        retval[kwargs['nick']] = LJUser(**kwargs)

    return retval


class OPMLOutline:
    def __init__(self, text, xmlURL, htmlURL, login):
        self.text = text
        self.xmlURL = xmlURL
        self.htmlURL = htmlURL
        self.login = login


def get_opml(user):
    """
    Returns dict{'communities': dict{ljuser -> `OPMLOutline'},
                 'users':       dict{ljuser -> `OPMLOutline'}}
    Only entries with URLs are returned.
    Livejournal does not export friends-groups due to privacy reasons.
    """
    fd = cached_urlopen('http://www.livejournal.com/tools/opml.bml?' + urlencode({'user': user}))
    return parse_opml(fd, user)

def parse_opml(fd, user=None):
    retval = {'communities': {}, 'users': {}}
    # LiveJournal can produce OPML file that is not UTF-8/strict cutting
    # feed description at the middle of character. This hack fixes it.
    content = fd.read().decode('utf-8', 'replace')
    content, errors = re.subn(ur'(\btext="[^"]*\ufffd) ', ur'\1" ', content)
    if errors:
        logging.warning("LJ: user <%s> has bad opml file, %i errors fixed."
                        % (user, errors))
    content = content.encode('utf-8')
    tree = ElementTree.XML(content)
    for el in tree.findall('.//outline'):
        xmlURL = el.get('xmlURL', None)
        text = el.get('text', None)
        if xmlURL is not None and text is not None:
            regexp_list = (r'(http://community.livejournal.com/([_0-9a-zA-Z]+))/data',
                           r'(http://users.livejournal.com/([_0-9a-zA-Z]+))/data',
                           r'(http://([-0-9a-zA-Z]+).livejournal.com)/data')
            for i, regexp in enumerate(regexp_list):
                m = re.match(regexp, xmlURL)
                if m:
                    sort = 'communities' if i == 0 else 'users'
                    htmlURL, login = m.group(1), m.group(2).replace('-', '_')
                    retval[sort][login] = OPMLOutline(text, xmlURL, htmlURL, login)
    return retval


def is_valid_login(user):
    return user.replace('_', '').isalnum()

def is_valid_password(password):
    # password is 7-bit, there are more validation rules at
    # http://www.livejournal.com/support/faqbrowse.bml?faqid=71
    try:
        p = str(password)
    except UnicodeEncodeError:
        return False
    return p and p == password


# vim:set tabstop=4 softtabstop=4 shiftwidth=4: 
# vim:set expandtab: 
