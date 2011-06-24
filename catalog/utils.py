# -*- coding: utf-8 -*-
from django.db.models import loading, Q
from catalog import settings as catalog_settings
from django.conf import settings
import warnings


def connected_models():
    for model_str in catalog_settings.CATALOG_MODELS:
        if type(model_str) in (list, tuple):
            applabel = model_str[0]
            model_name = model_str[1]
            warnings.warn(
                'CATALOG_MODELS setting should have new format, like: ("defaults.Item", "defaults.Section")',
                DeprecationWarning
            )
            yield loading.cache.get_model(applabel, model_name)
        else:
            yield loading.cache.get_model(*model_str.split('.'))

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
                PendingDeprecationWarning
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
