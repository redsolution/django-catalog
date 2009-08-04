from django.conf.urls.defaults import patterns, url
from catalog.admin.views import catalog_index, close_popup, add_section, edit_related
from catalog.admin.json import (tree, list, move_node, visible, delete_items, 
    RelativeTree)

urlpatterns = patterns('',
    url(r'^$', catalog_index),
    url(r'^new$', add_section),
    url(r'^item/(\d{1,7})/rel/$', edit_related),
    url(r'^json/tree$', tree),
    url(r'^json/list$', list),
    url(r'^json/move$', move_node),
    url(r'^json/visible$', visible),
    url(r'^json/delete$', delete_items),
    url(r'^json/relative/(\d{1,7})/$', RelativeTree().tree),
    url(r'^json/relative/(\d{1,7})/save/$', RelativeTree().save),
    url(r'^forms/closepopup$', close_popup),
)
