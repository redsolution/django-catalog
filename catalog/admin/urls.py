from django.conf.urls.defaults import patterns, url
from catalog.admin.views import catalog_index, close_popup, add_section
from catalog.admin.json import tree, list, move_node, visible, delete_items

urlpatterns = patterns('',
    url(r'^$', catalog_index),
    url(r'^new$', add_section),
    url(r'^json/tree$', tree),
    url(r'^json/list$', list),
    url(r'^json/move$', move_node),
    url(r'^json/visible$', visible),
    url(r'^json/delete$', delete_items),
    url(r'^forms/closepopup$', close_popup),
)
