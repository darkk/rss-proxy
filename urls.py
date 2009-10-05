# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from rssproxy.news import SiteNews

urlpatterns = patterns('',
    (r'^feed/(?P<code>[-_=a-zA-Z0-9]*)', 'rssproxy.views.get_feed'),

    (r'^feeds/(?P<url>.*)$', 'django.contrib.syndication.views.feed',
        {'feed_dict': {'sitenews': SiteNews}}),

    (r'^sitenews$', 'rssproxy.news.sitenews'),

    (r'^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'main.html'}),

    (r'^livejournal$', 'rssproxy.views.lj_dispatcher'),

    (r'^faq$', 'django.views.generic.simple.direct_to_template',
        {'template': 'faq.html'}),

    (r'^contacts$', 'django.views.generic.simple.direct_to_template',
        {'template': 'contacts.html'}),

    (r'^generic$', 'rssproxy.views.generic_mkfeed'),
)
