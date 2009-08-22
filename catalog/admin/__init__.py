# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from catalog.models import TreeItem, Section, Item, TreeItemImage, MetaItem
from django.http import Http404, HttpResponse
from django.utils.html import escape
from django.contrib.admin.widgets import FilteredSelectMultiple
from catalog.admin.utils import get_connected_models
from django.contrib.contenttypes import generic


class ImageInline(generic.GenericTabularInline):
    extra = 2
    model = TreeItemImage

class ItemAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    raw_id_fields = ('relative', 'sections')
    prepopulated_fields = {'slug': ('name',)}
    model = Item


class SectionAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Section


class CatalogAdminMix(admin.ModelAdmin):
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
for model_class, admin_class in get_connected_models():
    class CatalogModelAdmin(admin_class, CatalogAdminMix):
        pass
    try:
        admin.site.register(model_class, CatalogModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass
