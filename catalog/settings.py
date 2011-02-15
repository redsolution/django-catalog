from django.conf import settings
import os.path
import sys

DEFAULT_CATALOG_CONNECTED_MODELS = [
    ('defaults.models.Item', 'defaults.admin.ItemAdmin'),
    ('defaults.models.Section', 'defaults.admin.SectionAdmin'),
    ('defaults.models.MetaItem', None),
]

DEFAULT_TINYMCE = 'tinymce' in settings.INSTALLED_APPS
CATALOG_TINYMCE = getattr(settings, 'CATALOG_TINYMCE', DEFAULT_TINYMCE)

DEFAULT_MPTT = 'mptt' in settings.INSTALLED_APPS
CATALOG_MPTT = getattr(settings, 'CATALOG_MPTT', DEFAULT_MPTT)

DEFAULT_IMAGEKIT = 'imagekit' in settings.INSTALLED_APPS
CATALOG_IMAGEKIT = getattr(settings, 'CATALOG_IMAGEKIT', DEFAULT_IMAGEKIT)

# how urls will look like
# you may set 'id' or 'slug' values 
CATALOG_URL_SHEME = getattr(settings, 'CATALOG_URL_SHEME', 'id')
CATALOG_ROOT_PAGE = getattr(settings, 'CATALOG_ROOT_PAGE', True)

EXTRA_ORDER = getattr(settings, 'CATALOG_EXTRA_ORDER', False)

TEST = getattr(settings, 'TEST', None)
if TEST is None:
    if sys.argv[1] == 'test':
        TEST = True
    else:
        TEST = False

if TEST:
    CATALOG_CONNECTED_MODELS = DEFAULT_CATALOG_CONNECTED_MODELS
else:
    CATALOG_CONNECTED_MODELS = getattr(settings, 'CATALOG_CONNECTED_MODELS', DEFAULT_CATALOG_CONNECTED_MODELS)
