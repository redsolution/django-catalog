# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<slug>.*)-(?P<item_id>\d{1,7})/$', 'catalog.views.tree', name='tree'),
)
