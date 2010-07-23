from catalog.admin.ext import catalog_admin_site

temp_patterns = urlpatterns
urlpatterns = patterns('',
    (r'^admin/catalog/', include(catalog_admin_site.urls))
) + temp_patterns

urlpatterns += patterns('',
    (r'^catalog/', include('catalog.urls'))
)

# TODO: Sitemap
