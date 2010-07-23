from grandma.make import BaseMake
from grandma.models import GrandmaSettings
from catalog.grandma_setup.models import CatalogSettings
from os.path import dirname, join
import shutil


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
        }, 'w')


    def postmake(self):
        super(Make, self).postmake()
        if 'grandma.django-server-config' not in self.grandma_settings.installed_packages:
            catalog_media_dir = join(dirname(dirname(__file__)), 'media')
            project_media_dir = join(self.grandma_settings.project_dir, 'media')

#           WARNING! Silently delete media dirs
            try:
                shutil.rmtree(join(project_media_dir, 'extjs'))
#            no such directory
            except OSError:
                pass
            try:
                shutil.rmtree(join(project_media_dir, 'catalog'))
            except OSError:
                pass
#           copy files to media directory
            shutil.copytree(
                join(catalog_media_dir, 'catalog'),
                join(project_media_dir, 'catalog'),
            )
            shutil.copytree(
                join(catalog_media_dir, 'extjs'),
                join(project_media_dir, 'extjs'),
            )

#        if 'grandma.django-menu-proxy' in self.grandma_settings.installed_packages:
#            grandma_settings.render_to('settings.py', 'catalog/grandma/settings_menu.py')
