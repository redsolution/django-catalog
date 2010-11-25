# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('defaults.views',
    url(r'^visible/$', 'visible'),
)
