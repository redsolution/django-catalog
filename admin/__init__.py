# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes import generic
from utils.register import register_model
from catalog.models import TreeItem, Section, Item, ItemImage
from django.forms.models import inlineformset_factory
from django.http import Http404, HttpResponse
from django.utils.html import escape


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
    inlines = [TreeItemForItemInline, ItemImageInline]

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

register_model(Item, ItemOptions)


class SectionOptions(admin.ModelAdmin):
    model = Section
    inlines = [TreeItemForSectionInline, ItemImageInline]
    list_display = ('__unicode__', 'is_meta_item')
    
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

register_model(Section, SectionOptions)


class TreeItemOptions(admin.ModelAdmin):
    model = TreeItem

register_model(TreeItem, TreeItemOptions)
