# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, handler404, handler500, url
from django.conf import settings
from catalog.urls import urlpatterns

handler404
handler500

urlpatterns += patterns('',
    url(r'^sections/(?P<model>\w+)/(?P<slug>[-\w]+)/$', 'catalog.views.section_details', name='section_details'),
)
