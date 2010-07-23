from grandma.make import BaseMake
from grandma.models import GrandmaSettings
from catalog.grandma_setup.models import CatalogSettings
from os.path import dirname, join


class Make(BaseMake):
    grandma_settings = GrandmaSettings.objects.get_settings()

    def make(self):
        super(Make, self).make()
        catalog_settings = CatalogSettings.objects.get_settings()
        self.grandma_settings.render_to('settings.py', 'catalog/grandma/settings.py', {
            'catalog_settings': catalog_settings,
        })
        self.grandma_settings.render_to('urls.py', 'catalog/grandma/urls.py', {
            'catalog_settings': catalog_settings,
        })
        self.grandma_settings.render_to(['..', 'templates', 'admin', 'index.html'],
            'catalog/grandma/admin_index.html', {
            'catalog_settings': catalog_settings,
        })

