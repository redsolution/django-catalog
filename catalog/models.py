# -*- coding: utf-8 -*-

from django.db import models
from tinymce.models import HTMLField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from catalog.fields import RelatedField
from catalog import settings as catalog_settings
from imagekit.models import ImageModel
import mptt


class TreeItem(models.Model):
    class Meta:
        verbose_name = u'Элемент каталога'
        verbose_name_plural = u'Элементы каталога'
        ordering = ['tree_id', 'lft']

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=u'Родительский', null=True, blank=True, editable=False)

    @models.permalink
    def get_absolute_url(self):
        return ('catalog.views.tree', (), {'item_id': self.id, 'slug': self.get_slug()})
    
    def get_slug(self):
        return u'slug'
    
    def get_type(self):
#        TODO: retrieve type from FK
        pass

    def delete(self, *args, **kwds):
#        TODO: Do we really need this?
        pass
    # template security
    delete.alters_data = True

    def __unicode__(self):
        return self.name

try:
    mptt.register(TreeItem, tree_manager_attr='objects')
except mptt.AlreadyRegistered:
    pass



class Section(models.Model):
    class Meta:
        verbose_name = u"Раздел каталога"
        verbose_name_plural = u'Разделы каталога'
    
    tree = models.OneToOneField('TreeItem', blank=True, null=True)
    
    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    short_description = models.TextField(verbose_name=u'Краткое описание', null=True, blank=True)
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)

   # fields required for SEO
    seo_title = models.CharField(verbose_name=u'SEO заголовок', max_length=200, null=True, blank=True)
    seo_description = models.TextField(verbose_name=u'SEO описание', null=True, blank=True)
    seo_keywords = models.CharField(verbose_name=u'SEO ключевые слова', max_length=200, null=True, blank=True)

    # Section fields
    is_meta_item = models.BooleanField(verbose_name=u'Мета товар', default=False)
    
    def has_nested_sections(self):
        return bool(len(self.tree.children.filter(section__isnull=False,
            section__is_meta_item=False)))

    def min_price(self):
        # FIXME: If children are not Item instances?
        return min([child.item.price for child in self.tree.children.all()])

    def __unicode__(self):
        return self.name


class Item(models.Model):
    class Meta:
        verbose_name = u"Продукт каталога"
        verbose_name_plural = u'Продукты каталога'
        
    tree = models.OneToOneField('TreeItem', blank=True, null=True)

    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    short_description = models.TextField(verbose_name=u'Краткое описание', null=True, blank=True)
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)

    # fields required for SEO
    seo_title = models.CharField(verbose_name=u'SEO заголовок', max_length=200, null=True, blank=True)
    seo_description = models.TextField(verbose_name=u'SEO описание', null=True, blank=True)
    seo_keywords = models.CharField(verbose_name=u'SEO ключевые слова', max_length=200, null=True, blank=True)
    
    # Item fields
    # Relation options
    relative = RelatedField('Item', verbose_name=u'Сопутствующие товары', null=True, blank=True, related_name='relative')
    sections = RelatedField('Section', verbose_name=u'Разделы', null=True, blank=True, related_name='items')

    # Sale options
    price = models.DecimalField(verbose_name=u'Цена', null=True, blank=True, max_digits=12, decimal_places=2)
    identifier = models.CharField(verbose_name=u'Артикул', max_length=50, blank=True, default='')
    barcode = models.CharField(verbose_name=u'Штрих-код', max_length=50, null=True)
    quantity = models.IntegerField(verbose_name=u'Остаток на складе',
        help_text=u'Введите 0 если на складе нет товара', null=True, blank=True)
    
    def __unicode__(self):
        return self.name


class TreeItemImage(ImageModel):
    image = models.ImageField(verbose_name=u'Изображение',
        upload_to='upload/catalog/itemimages/%Y-%m-%d')

    tree = models.ForeignKey('TreeItem', blank=True, null=True)
    
    class IKOptions:
        cache_dir = 'upload/cache'
        # other by default

    def __unicode__(self):
        return self.image.url