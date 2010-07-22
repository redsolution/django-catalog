# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from catalog.admin import register, CatalogAdmin
from catalog.defaults.models import Item, Section, CatalogImage


class ImageInline(generic.GenericTabularInline):
    extra = 2
    model = CatalogImage


class ItemAdmin(CatalogAdmin):
    inlines = [ImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Item
    # ext catalog
    tree_text_attr = 'name'
    tree_leaf = True
    catalog_fields = ['name', 'slug']
    m2ms = []


class SectionAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Section
    # ext catalog
    tree_text_attr = 'name'
    tree_leaf = False
    catalog_fields = ['name', 'slug']
    m2ms = []

register(Item, ItemAdmin)
register(Section, SectionAdmin)
