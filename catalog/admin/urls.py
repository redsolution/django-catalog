from django.conf.urls.defaults import patterns, url
from catalog.admin.json import RelativeTree, SectionsTree, ItemsTree
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('catalog.admin',
    url(r'^$', direct_to_template, {'template': 'admin/catalog/main.html'}),
    url(r'^/closepopup$', direct_to_template, {'template': 'admin/catalog/closepopup.html'}),

    url(r'^new(?P<model_name>\w+)$', 'views.add_instance'),
    url(r'^item/(\d{1,7})/rel/$', 'views.edit_item_related'),
    url(r'^section/(\d{1,7})/rel/$', 'views.edit_section_related'),
    url(r'^edititem/(\d{1,7})/$', 'views.editor_redirect'),
    url(r'^relations/(\d{1,7})/$', 'views.related_redirect'),
    url(r'^view/(\d{1,7})/$', 'views.absolute_url_redirect'),

    url(r'^json/tree$', 'json.tree'),
    url(r'^json/list$', 'json.list'),
    url(r'^json/move$', 'json.move_node'),
    url(r'^json/visible$', 'json.visible'),
    url(r'^json/delete$', 'json.delete_items'),
    url(r'^json/count/delete$', 'json.delete_count'),

    url(r'^json/relative/(\d{1,7})/$', RelativeTree.tree),
    url(r'^json/relative/(\d{1,7})/save/$', RelativeTree.save),
    url(r'^json/sections/(\d{1,7})/$', SectionsTree.tree),
    url(r'^json/sections/(\d{1,7})/save/$', SectionsTree.save),
    url(r'^json/items/(\d{1,7})/$', ItemsTree.tree),
    url(r'^json/items/(\d{1,7})/save/$', ItemsTree.save),
)
