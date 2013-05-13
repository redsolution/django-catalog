from catalog.models import TreeItem
from catalog.utils import get_q_filters, connected_models
from django.contrib.sitemaps import GenericSitemap


class CatalogSitemap(GenericSitemap):
    """
    Catalog sitemap.

    Sets 'queryset' according to filter settings.
    Sets 'date_field' if 'last_modified' exists in model.
    """

    def __init__(self, model, priority=None, changefreq=None):
        info_dict = {
            'queryset': model.objects.filter(get_q_filters()[model])
        }
        if model._meta.get_field('last_modified'):
            info_dict['date_field'] = 'last_modified'
        super(CatalogSitemap, self).__init__(
            info_dict=info_dict, priority=priority, changefreq=changefreq)


def get_sitemaps():
    """
    :return: Dictionary with `CatalogSitemap` for each registered model.
    """
    sitemaps = {}
    for model in connected_models():
        sitemaps['%s.%s' % (
            model._meta.app_label, model._meta.module_name)] = CatalogSitemap(model)
    return sitemaps
