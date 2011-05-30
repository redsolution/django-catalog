from django.conf import settings

UPLOAD_ROOT = getattr(settings, 'UPLOAD_ROOT', 'upload')

from django.db.models import Q
settings.CATALOG_FILTERS = Q(show=True)