# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.contenttypes import generic
from catalog.models import TreeItem, Section, Item, ItemImage
from django.forms.models import inlineformset_factory
from django.http import Http404, HttpResponse
from django.utils.html import escape
from django.contrib.admin.widgets import FilteredSelectMultiple

# Inlines

class ItemImageInline(generic.GenericStackedInline):
    model = ItemImage
    exclude = ('thumb',)

class TreeItemForSectionInline(admin.StackedInline):
    model = TreeItem
    prepopulated_fields = {'slug': ('name',)}
    exclude = ('item', 'parent')

# this is help class for usage in default admin interface
class TreeItemForItemInline(admin.StackedInline):
    model = TreeItem
    prepopulated_fields = {'slug': ('name',)}
    exclude = ('section',)

# ModelAdmin classes

class ItemOptions(admin.ModelAdmin):
    model = Item
#    filter_horizontal = ('relative', 'sections')
    inlines = [TreeItemForItemInline, ItemImageInline]
    search_fields = ('tree__name', 'tree__short_description')
    
    def response_change(self, request, obj):
        """
        Wrapper around Django ModelAdmin method to provide
        popup close on edit item
        """
        if ('_continue' not in request.POST) and ('_popup' in request.POST):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(pk_value), escape(obj))) # escape() calls force_unicode.
        return super(ItemOptions, self).response_change(request, obj)

try:
    admin.site.register(Item, ItemOptions)
except AlreadyRegistered:
    pass


class SectionOptions(admin.ModelAdmin):
    model = Section
    inlines = [TreeItemForSectionInline, ItemImageInline]
    list_display = ('__unicode__', 'is_meta_item')
    search_fields = ('tree__name', 'tree__short_description')
    
    def response_change(self, request, obj):
        """
        Wrapper around Django ModelAdmin method to provide
        popup close on edit item
        """
        if ('_continue' not in request.POST) and ('_popup' in request.POST):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(pk_value), escape(obj))) # escape() calls force_unicode.
        return super(SectionOptions, self).response_change(request, obj)

try:
    admin.site.register(Section, SectionOptions)
except AlreadyRegistered:
    pass


class TreeItemOptions(admin.ModelAdmin):
    model = TreeItem
    search_fields = ('name',)

try:
    admin.site.register(TreeItem, TreeItemOptions)
except AlreadyRegistered:
    pass
