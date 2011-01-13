from redsolutioncms.make import BaseMake
from redsolutioncms.models import CMSSettings
from os.path import dirname, join


class Make(BaseMake):
    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to('settings.py', 'catalog/redsolutioncms/settings.pyt')
        cms_settings.save()

make = Make()
