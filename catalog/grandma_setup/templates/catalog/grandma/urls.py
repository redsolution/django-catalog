urlpatterns += patterns('',
    (r'^catalog/', include('catalog.urls'))
)

# TODO: Sitemap

#catalog_dict = {
#    'queryset': News.objects.filter(show=True),
#    'date_field': 'date',
#}
#sitemaps['news'] = GenericSitemap(news_dict),
