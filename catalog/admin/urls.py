from django.conf.urls.defaults import patterns, url
from catalog.admin.views import (catalog_index, close_popup, add_section,
    edit_related, editor_redirect, add_item)
from catalog.admin.json import (tree, list, move_node, visible, delete_items, delete_count,
    RelativeTree, SectionsTree)

urlpatterns = patterns('',
    url(r'^$', catalog_index),
    url(r'^newsection$', add_section),
    url(r'^newitem$', add_item),
    url(r'^item/(\d{1,7})/rel/$', edit_related),
    url(r'^edititem/(\d{1,7})/$', editor_redirect),
    url(r'^json/tree$', tree),
    url(r'^json/list$', list),
    url(r'^json/move$', move_node),
    url(r'^json/visible$', visible),
    url(r'^json/delete$', delete_items),
    url(r'^json/count/delete$', delete_count),
    url(r'^json/relative/(\d{1,7})/$', RelativeTree().tree),
    url(r'^json/relative/(\d{1,7})/save/$', RelativeTree().save),
    url(r'^json/sections/(\d{1,7})/$', SectionsTree().tree),
    url(r'^json/sections/(\d{1,7})/save/$', SectionsTree().save),
    url(r'^forms/closepopup$', close_popup),
)
