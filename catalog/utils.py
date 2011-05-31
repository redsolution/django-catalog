# -*- coding: utf-8 -*-
from django.db.models import loading, Q
from catalog import settings as catalog_settings
from django.conf import settings


def connected_models():
    for app_label, model_name in catalog_settings.CATALOG_MODELS:
        yield loading.cache.get_model(app_label, model_name)

def get_data_appnames():
    app_labels = set()
    for app_label, model_name in catalog_settings.CATALOG_MODELS:
        app_labels.update([app_label, ])
    return app_labels

def get_q_filters():
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
