# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from catalog.grandma_setup.admin import CatalogSettingsAdmin


admin_instance = CatalogSettingsAdmin()

urlpatterns = patterns('',
    url(r'^$', admin_instance.change_view, name='catalog_index'),
)
