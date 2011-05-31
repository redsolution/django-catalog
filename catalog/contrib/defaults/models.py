# -*- coding: utf-8 -*-
from catalog import settings as catalog_settings
from catalog.contrib.defaults.settings import UPLOAD_ROOT
#from catalog.models import TreeItem
from catalog.base import CatalogBase 
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink

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
    slug = models.SlugField(verbose_name=_('Slug'), max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(verbose_name=_('Section description'), null=True, blank=True)
    
    def get_absolute_url(self):
        try:
            # test if catalog-by-slug installed
            reverse('catalog-by-slug', kwargs={'model': 'model', 'slug': 'slug'})
        except NoReverseMatch:
            pass
        else:
            return reverse('catalog-by-slug', kwargs={
                'model': self.__class__.__name__.lower(),
                'slug': self.slug,
            })
        try:
            reverse('catalog-by-id', kwargs={'slug': 'slug', 'object_id': '1'})
        except NoReverseMatch:
            pass
        else:
            return reverse('catalog-by-id', kwargs={
                'slug': self.slug,
                'object_id': self.tree.get().id,
            })
        raise NoReverseMatch('No appropriate methods found, take a look in the code')


class Section(CommonFields, models.Model):
    leaf = False
    
    class Meta:
        verbose_name = _('Catalog section')
        verbose_name_plural = _('Catalog sections')

    def __unicode__(self):
        return self.name


class Item(CommonFields, models.Model):
    leaf = True
    
    class Meta:
        verbose_name = _('Catalog item')
        verbose_name_plural = _('Catalog items')

    # Sale options
    article = models.CharField(verbose_name=_('Item article'), null=True, blank=True, max_length=30)
    price = models.DecimalField(verbose_name=_('Item price'), null=True, blank=True, max_digits=12, decimal_places=2)
    quantity = models.IntegerField(verbose_name=_('Item quantity'),
        help_text=_('Enter 0 if you have no items. Item will be automatically hidden'), null=True, blank=True)
    
    new = models.BooleanField(verbose_name=_('Newest'), default=False)

    def __unicode__(self):
        return self.name

class CatalogImage(ImageModel):
    class Meta:
        verbose_name = _('Generic catalog image')
        verbose_name_plural = _('Generic catalog images')
    
    image = models.ImageField(verbose_name=_('Image'),
        upload_to=join(UPLOAD_ROOT, 'catalog'))

    content_type = models.ForeignKey(ContentType, related_name='default_catalogimages')
    object_id = models.PositiveIntegerField()
    # content object points to an object which belongs to the image 
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class IKOptions:
        cache_dir = join(UPLOAD_ROOT, 'cache/catalog')
        spec_module = 'catalog.contrib.defaults.ikspecs'
        cache_filename_format = "%(filename)s-%(specname)s.%(extension)s"

    def __unicode__(self):
        if self.image:
            return self.image.url
        else:
            return 'image deleted'
