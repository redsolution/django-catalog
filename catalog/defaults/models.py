# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from catalog.models import TreeItem, Base
from catalog import settings as catalog_settings
from django.utils.translation import ugettext_lazy as _
from catalog.defaults import settings as catalog_default_settings

# fake tinymce
if catalog_settings.CATALOG_TINYMCE:
    from tinymce.models import HTMLField
else:
    from django.forms import Textarea as HTMLField

# fake imagekit
if catalog_settings.CATALOG_IMAGEKIT:
    from imagekit.models import ImageModel
else:
    from django.db.models import Model as ImageModel


class OverridenBase(Base):
    '''Common for all objects fields'''
    class Meta:
        abstract = True

    images = generic.GenericRelation('CatalogImage')

    # Primary options
    slug = models.SlugField(verbose_name=_('Slug'), max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=_('Name'), max_length=200, default='')
    description = models.TextField(verbose_name=_('Full description'), null=True, blank=True)
    # Visibility
    visible = models.BooleanField(verbose_name=_('Item is visivble'), default=True)

    def get_absolute_url(self):
        return self.tree.get().get_absolute_url()

    def __unicode__(self):
        return self.name


class Item(OverridenBase):
    class Meta:
        verbose_name = _('Catalog item')
        verbose_name_plural = _('Catalog items')

    # Sale options
    price = models.DecimalField(verbose_name=u'Цена', null=True, blank=True, max_digits=12, decimal_places=2)

    exclude_children = [u'item', u'section']  # this field, will be removed in future


class Section(OverridenBase):
    class Meta:
        verbose_name = _('Catalog section')
        verbose_name_plural = _('Catalog sections')


class CatalogImage(ImageModel):
    class Meta:
        verbose_name = _('Catalog Image')
        verbose_name_plural = _('Catalog images')

    class IKOptions:
        cache_filename_format = "%(filename)s-%(specname)s.%(extension)s"
        spec_module = 'catalog.defaults.ikspec'
        cache_dir = catalog_default_settings.UPLOAD_PATH + 'catalog/cache/'

    image = ImagePreviewField(verbose_name=_('Image'),
        upload_to=catalog_default_settings.UPLOAD_PATH + 'catalog/source')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        if self.image:
            return os.path.basename(self.image.url)
        else:
            return _('Deleted image')
