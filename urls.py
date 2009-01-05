# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^feed/(?P<code>[-_=a-zA-Z0-9]*)', 'rssproxy.views.get_feed'),
    (r'^livejournal/opml$', 'rssproxy.views.lj_opml_get'),
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'main.html'}),
)
