# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^feed/(?P<code>[-_=a-zA-Z0-9]*)', 'rssproxy.views.get_feed'),

    # FIXME: obsolete
    (r'^livejournal/opml$', 'rssproxy.views.lj_opml_get'),

    (r'^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'main.html'}),

    (r'^livejournal$', 'rssproxy.views.lj_dispatcher'),

    (r'^faq$', 'django.views.generic.simple.direct_to_template',
        {'template': 'faq.html'}),

    (r'^contacts$', 'django.views.generic.simple.direct_to_template',
        {'template': 'contacts.html'}),

    (r'^generic$', 'rssproxy.views.generic_mkfeed'),
)
