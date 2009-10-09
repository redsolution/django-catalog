#### Admin classes ###
from django.contrib import admin
from django.contrib.contenttypes import generic
from defaults.models import Item, Section, MetaItem, TreeItemImage
from catalog.admin import register

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


#### Ext Admin classes ###
from catalog.admin.ext import BaseExtAdmin

class ItemExtAdmin(BaseExtAdmin):
    tree_text_attr = 'name'
    fields = ('name',)
    m2ms = ('relative',)

class SectionExtAdmin(BaseExtAdmin):
    tree_text_attr = 'name'
    fields = ('name', 'slug')
    m2ms = ('items',)

register(Item, ItemAdmin, ItemExtAdmin)
register(Section, SectionAdmin, SectionExtAdmin)
