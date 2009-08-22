from django.conf.urls.defaults import patterns, url
from catalog.admin.json import RelativeTree, SectionsTree

urlpatterns = patterns('catalog.admin',
    url(r'^$', 'views.catalog_index'),
    url(r'^newsection$', 'views.add_section'),
    url(r'^newitem$', 'views.add_item'),
    url(r'^newmetaitem$', 'views.add_metaitem'),
    url(r'^item/(\d{1,7})/rel/$', 'views.edit_related'),
    url(r'^edititem/(\d{1,7})/$', 'views.editor_redirect'),
    url(r'^json/tree$', 'json.tree'),
    url(r'^json/list$', 'json.list'),
    url(r'^json/move$', 'json.move_node'),
    url(r'^json/visible$', 'json.visible'),
    url(r'^json/delete$', 'json.delete_items'),
    url(r'^json/count/delete$', 'json.delete_count'),
    url(r'^json/relative/(\d{1,7})/$', RelativeTree().tree),
    url(r'^json/relative/(\d{1,7})/save/$', RelativeTree().save),
    url(r'^json/sections/(\d{1,7})/$', SectionsTree().tree),
    url(r'^json/sections/(\d{1,7})/save/$', SectionsTree().save),
    url(r'^forms/closepopup$', 'views.close_popup'),
)
