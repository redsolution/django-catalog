# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from models import Item, Section, CatalogImage


class CatalogImageInline(generic.GenericTabularInline):
    model = CatalogImage
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Item


class SectionAdmin(admin.ModelAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Section


admin.site.register(Item, ItemAdmin)
admin.site.register(Section, SectionAdmin)
