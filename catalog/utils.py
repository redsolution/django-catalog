# -*- coding: utf-8 -*-

import warnings

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import loading, Q

from catalog import settings as catalog_settings


def connected_models():
    """
    Returns list of registered catalog models.
    """
    for model_str in catalog_settings.CATALOG_MODELS:
        if type(model_str) in (list, tuple):
            applabel = model_str[0]
            model_name = model_str[1]
            warnings.warn(
                'CATALOG_MODELS setting should have new format, like: ("defaults.Item", "defaults.Section")',
                DeprecationWarning
            )
            model_cls = loading.cache.get_model(applabel, model_name)
        else:
            model_cls = loading.cache.get_model(*model_str.split('.'))

        if model_cls is None:
            warnings.warn(
                'Can not import model %s from app %s, '
                'check CATALOG_MODELS setting, **YOU MAY LOSE DATA!**' % (
                    model_cls.__name__, model_cls._meta.app_label))
        yield model_cls


def get_data_appnames():
    '''
    Returns app labales from connected models, for example:
    ['defaults',] or ['custom_catalog',] or ['defaults', 'custom_catalog']
    '''
    app_labels = set()
    for model_str in catalog_settings.CATALOG_MODELS:
        if type(model_str) in (list, tuple):
            app_label = model_str[0]
            warnings.warn(
                'CATALOG_MODELS setting should have new format, like: ("defaults.Item", "defaults.Section")',
                DeprecationWarning
            )
        else:
            app_label, _ = model_str.split('.')
        app_labels.update([app_label, ])
    return app_labels


def get_q_filters():
    '''
    Internal utility, returns dictionary with following content:
    {'app_label.model_name': model_query}
    where model_query is django ``Q`` object
    '''
    q_filters = {}
    for model_cls in connected_models():
        q_filters[model_cls] = None

    CATALOG_FILTERS = getattr(settings, 'CATALOG_FILTERS', None)
    if getattr(settings, 'CATALOG_FILTERS', None) is not None:
        # Check if CATALOG_FILTERS has nested dictionaries
        if any([isinstance(val, dict) for val in CATALOG_FILTERS.values()]):
            # Apply filter per-model
            for model_str, model_filter in CATALOG_FILTERS.iteritems():
                model_cls = loading.cache.get_model(*model_str.split('.'))
                q_filters[model_cls] = Q(**model_filter)
        else:
            # Apply filter to all models
            global_filter = CATALOG_FILTERS
            for key in q_filters.iterkeys():
                q_filters[key] = Q(**global_filter)
    return q_filters


def get_sorted_items(queryset):
    """
    Resort content objects in tree order.

    :param queryset: queryset with catalog instances.
    :return: new list instance.
    """
    from catalog.models import TreeItem
    content_type = ContentType.objects.get_for_model(queryset.model)
    objects = dict([(instance.id, instance) for instance in queryset])
    items = TreeItem.tree.get_query_set().filter(
        content_type=content_type, object_id__in=objects.keys())
    ids = items.values_list('object_id', flat=True)
    return [objects[value] for value in ids]


def query_set_manager(query_set_class):
    """
    Creates new QuerySetManager instance based on ``query_set_class``.
    """

    class QuerySetManager(models.Manager):

        def get_query_set(self):
            return query_set_class(self.model, using=self._db)

        def __getattr__(self, attr, *args):
            try:
                return getattr(self.__class__, attr, *args)
            except AttributeError, e:
                if attr.startswith('__') and attr.endswith('__'):
                    raise e
                return getattr(self.get_query_set(), attr, *args)

    return type(query_set_class.__name__ + 'Manager', (QuerySetManager,), {})()
