from django.conf import settings
from django.conf.urls.defaults import *
from staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('catalog.urls.by_slug')),
)

