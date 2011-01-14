# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, handler404, handler500, url
from django.conf import settings

handler404
handler500

urlpatterns = patterns('',
    url(r'^$', 'catalog.views.root', name='catalog-root'),
)
