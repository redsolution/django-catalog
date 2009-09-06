from django.conf import settings
import os.path
import sys


DEFAULT_CATALOG_CONNECTED_MODELS = [
    ('catalog.models.Item', 'catalog.admin.ItemAdmin'),
    ('catalog.models.Section', 'catalog.admin.SectionAdmin'),
    ('catalog.models.MetaItem', None),
]
try:
    import mptt
    DEFAULT_USE_MPTT = True
except ImportError:
    DEFAULT_USE_MPTT = False

USE_MPTT = getattr(settings, 'USE_MPTT', DEFAULT_USE_MPTT)

DEFAULT_CATALOG_CONNECTED_MODELS = [
    ('catalog.defaults.Item', 'catalog.defaults.ItemAdmin'),
    ('catalog.defaults.Section', 'catalog.defaults.SectionAdmin'),
    ('catalog.defaults.MetaItem', None),
]

TEST = getattr(settings, 'TEST',  None)
if TEST is None:
    if sys.argv[1] == 'test':
        TEST = True
    else:
        TEST = False

if TEST:
    CATALOG_CONNECTED_MODELS = DEFAULT_CATALOG_CONNECTED_MODELS
else:
    CATALOG_CONNECTED_MODELS = getattr(settings, 'CATALOG_CONNECTED_MODELS', DEFAULT_CATALOG_CONNECTED_MODELS)
