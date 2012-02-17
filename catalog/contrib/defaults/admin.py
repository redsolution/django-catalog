# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from models import Item, Section, CatalogImage
from catalog.admin import CatalogAdmin

class CatalogImageInline(generic.GenericTabularInline):
    model = CatalogImage
    extra = 1


class ItemAdmin(CatalogAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Item


class SectionAdmin(CatalogAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Section
    list_display = ('name', 'slug', 'description', 'show')
    

admin.site.register(Item, ItemAdmin)
admin.site.register(Section, SectionAdmin)
