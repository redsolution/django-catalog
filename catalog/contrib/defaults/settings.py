from django.conf import settings

UPLOAD_ROOT = getattr(settings, 'UPLOAD_ROOT', 'upload')

#settings.CATALOG_FILTERS = dict(show=True)
