# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.http import Http404, HttpResponse
from django.utils.html import escape
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes import generic

from catalog.models import TreeItem
from catalog.admin.utils import get_connected_models
from catalog.admin.ext import ext_site, BaseExtAdmin


class CatalogAdminMix(admin.ModelAdmin):
    
    prepopulated_fields = {'slug': ('name',)}
    
    def response_change(self, request, obj):
        """
        Wrapper around Django ModelAdmin method to provide
        popup close on *edit* item
        """
        if ('_continue' not in request.POST) and ('_popup' in request.POST):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(pk_value), escape(obj))) # escape() calls force_unicode.
        return super(TreeItemAdmin, self).response_change(request, obj)

# register models
def register(model_class, admin_class, ext_admin_class=BaseExtAdmin):
    # register Django admin model
    class CatalogModelAdmin(admin_class, CatalogAdminMix):
        pass
    try:
        admin.site.register(model_class, CatalogModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass
    # register ext admin
    try:
        ext_site.register(model_class, ext_admin_class)
    except admin.sites.AlreadyRegistered:
        pass
