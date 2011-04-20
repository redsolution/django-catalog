from django.conf import settings
import os.path
import sys

# TODO: migrate to django.db.models.loader rather than import modules manually
CATALOG_MODELS = [
    ('defaults', 'Item'),
    ('defaults', 'Section'),
]

DEFAULT_MPTT = 'mptt' in settings.INSTALLED_APPS
CATALOG_MPTT = getattr(settings, 'CATALOG_MPTT', DEFAULT_MPTT)

# TODO: Extend existing SERIALIZATION_MODULES
settings.SERIALIZATION_MODULES = {
    'catalog_extdirect' : 'catalog.grid_to_json',
}
