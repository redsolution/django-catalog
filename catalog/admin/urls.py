from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from catalog.admin.ext import ext_site
from catalog.admin.utils import admin_permission_required


urlpatterns = patterns('catalog.admin',
    url(r'^$', admin_permission_required('caatalog.tree_item')(direct_to_template),
        {'template': 'admin/catalog/main.html'}),
    url(r'^/closepopup$', admin_permission_required('catalog.tree_item')(direct_to_template),
        {'template': 'admin/catalog/closepopup.html'}),

    url(r'^new/(?P<model_name>\w+)/$', 'views.add_instance'),

    url(r'^edititem/(\d{1,7})/$', 'views.editor_redirect'),
    url(r'^relations/(\d{1,7})/$', 'views.related_redirect'),
    url(r'^view/(\d{1,7})/$', 'views.absolute_url_redirect'),

    url(r'^(.*)$', ext_site.root),
)
