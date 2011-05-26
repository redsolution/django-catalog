# -*- coding: utf-8 -*-
from django.db.models import loading
from catalog import settings as catalog_settings


def connected_models():
    for app_label, model_name in catalog_settings.CATALOG_MODELS:
        yield loading.cache.get_model(app_label, model_name)

