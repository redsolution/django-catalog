# -*- coding: utf-8 -*-
from catalog.forms import LinkInsertionForm
from catalog.models import Link
from django import template
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from models import Item, Section, CatalogImage
from catalog.admin import CatalogAdmin

class CatalogImageInline(generic.GenericTabularInline):
    model = CatalogImage
    extra = 1


class LinkInline(generic.GenericTabularInline):
    model = Link
    form = LinkInsertionForm

class ItemAdmin(CatalogAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Item


class SectionAdmin(CatalogAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Section
    
    # override to show links
    add_form_template = 'admin/catalog/change_form_with_links.html'
    change_form_template = 'admin/catalog/change_form_with_links.html'
    

admin.site.register(Item, ItemAdmin)
admin.site.register(Section, SectionAdmin)
