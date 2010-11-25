from django.conf import settings
import os.path
import sys

DEFAULT_CATALOG_CONNECTED_MODELS = [
    ('catalog.contrib.defaults.models.Item', None),
    ('catalog.contrib.defaults.models.Section', None),
]
CATALOG_CONNECTED_MODELS = getattr(settings, 'CATALOG_CONNECTED_MODELS', DEFAULT_CATALOG_CONNECTED_MODELS)

DEFAULT_MPTT = 'mptt' in settings.INSTALLED_APPS
CATALOG_MPTT = getattr(settings, 'CATALOG_MPTT', DEFAULT_MPTT)
