# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from catalog.fields import RelatedField
from catalog.models import TreeItem, Base

from catalog import settings as catalog_settings

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


class Section(Base):
    class Meta:
        verbose_name = u"Раздел каталога"
        verbose_name_plural = u'Разделы каталога'

    images = generic.GenericRelation('TreeItemImage')

    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return self.tree.get().get_absolute_url()

    def __unicode__(self):
        return self.name


class MetaItem(Section):
    class Meta:
        verbose_name = u"Метатовар"
        verbose_name_plural = u'Метатовары'

    images = generic.GenericRelation('TreeItemImage')

    exclude_children = [u'section']

    @models.permalink
    def get_absolute_url(self):
        return self.tree.get().get_absolute_url_undecorated()


class Item(Base):
    class Meta:
        verbose_name = u"Продукт каталога"
        verbose_name_plural = u'Продукты каталога'

    images = generic.GenericRelation('TreeItemImage')

    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)

    # Item fields
    # Relation options
    relative = RelatedField('Item', verbose_name=u'Сопутствующие товары', null=True, blank=True, related_name='relative')
    sections = RelatedField('Section', verbose_name=u'Разделы', null=True, blank=True, related_name='items')

    # Sale options
    price = models.DecimalField(verbose_name=u'Цена', null=True, blank=True, max_digits=12, decimal_places=2)
    quantity = models.IntegerField(verbose_name=u'Остаток на складе',
        help_text=u'Введите 0 если на складе нет товара', null=True, blank=True)

    exclude_children = [u'item', u'section', u'metaitem']

    @models.permalink
    def get_absolute_url(self):
        return self.tree.get().get_absolute_url_undecorated()

    def __unicode__(self):
        return self.name

class TreeItemImage(ImageModel):
    image = models.ImageField(verbose_name=u'Изображение',
        upload_to='upload/catalog/itemimages/%Y-%m-%d')

    pallete = models.BooleanField(default=False, verbose_name=u'Палитра',
        help_text=u'Картинка будет отображаться в полном размере после описания')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class IKOptions:
        cache_dir = 'upload/catalog/cache'
        spec_module = 'defaults.ikspec'

    def __unicode__(self):
        return self.image.url
