from django.conf import settings
import os.path

# URL that handles catalog's media and uses <MEDIA_ROOT>/catalog by default.
CATALOG_MEDIA_URL = getattr(settings, 'CATALOG_MEDIA_URL', os.path.join(settings.MEDIA_URL, 'catalog/'))
