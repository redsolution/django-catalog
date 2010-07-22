from catalog.grandma_setup.models import CatalogSettings
from grandma.admin import GrandmaBaseAdmin


class CatalogSettingsAdmin(GrandmaBaseAdmin):
    model = CatalogSettings
