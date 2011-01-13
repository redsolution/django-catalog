# -*- coding: utf-8 -*-
from catalog import settings as catalog_settings
from catalog.contrib.defaults.settings import UPLOAD_ROOT
from catalog.models import TreeItem, CatalogBase
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from os.path import join
# fake TinyMCE
try:
    from tinymce.models import HTMLField
except ImportError:
    from django.forms import Textarea as HTMLField

# fake imagekit
try:
    from imagekit.models import ImageModel
except ImportError:
    from django.db.models import Model as ImageModel


class CommonFields(CatalogBase):
    class Meta:
        abstract = True
    
    images = generic.GenericRelation('CatalogImage')

    # Display options
    show = models.BooleanField(verbose_name=_('Show on site'), default=True)

    # Primary options
    name = models.CharField(verbose_name=_('Section name'), max_length=200, default='')
    slug = models.SlugField(verbose_name=_('Slug'), max_length=200, null=True, blank=True)
    description = models.TextField(verbose_name=_('Section description'), null=True, blank=True)


class Section(CommonFields, models.Model):
    class Meta:
        verbose_name = _('Catalog section')
        verbose_name_plural = _('Catalog sections')
    

    def __unicode__(self):
        return self.name


class Item(CommonFields, models.Model):
    class Meta:
        verbose_name = _('Catalog item')
        verbose_name_plural = _('Catalog items')

    # Sale options
    price = models.DecimalField(verbose_name=_('Item price'), null=True, blank=True, max_digits=12, decimal_places=2)
    quantity = models.IntegerField(verbose_name=_('Item quantity'),
        help_text=_('Enter 0 if you have no items. Item will be automatically hidden'), null=True, blank=True)

    def __unicode__(self):
        return self.name


class CatalogImage(ImageModel):
    class Meta:
        verbose_name = _('Generic catalog image')
        verbose_name_plural = _('Generic catalog images')
    
    image = models.ImageField(verbose_name=_('Image'),
        upload_to=join(UPLOAD_ROOT, 'catalog'))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    # content object points to an object which belongs to the image 
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class IKOptions:
        cache_dir = join(UPLOAD_ROOT, 'cache/catalog')

    def __unicode__(self):
        if self.image:
            return self.image.url
        else:
            return 'image deleted'
