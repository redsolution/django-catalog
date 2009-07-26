# -*- coding: utf-8 -*-

from django.db import models
from smartfiles.models import SmartFileModel
from tinymce.models import HTMLField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import mptt

THUMB_SIZE = (120, 120)


class ItemImage(SmartFileModel):
    file_rules = [ {
        'name': 'image',
        'image_check': True,
        'copy': 'thumb',
        'resize': True,
        'width': 200,
        'height': 200,
    }, {
        'name': 'thumb',
        'resize': True,
        'enlarge': True,
        'width': THUMB_SIZE[0],
        'height': THUMB_SIZE[1],
    } ]

    image = models.ImageField(verbose_name=u'Изображение',
        upload_to='upload/catalog/itemimages/%Y-%m-%d')
    thumb = models.ImageField(verbose_name=u'Превью',
        upload_to='upload/catalog/itemthumbs/%Y-%m-%d', editable=False)
    
    # Generic FK used because we want to make TreeItem editable in 
    # admin interface as inline, and include ItemImage too.     
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def thumb_padding_x(self):
        return (THUMB_SIZE[0] - self.thumb.width) / 2

    def thumb_padding_y(self):
        return (THUMB_SIZE[1] - self.thumb.height) / 2

    def __unicode__(self):
        return self.image.url


class TreeItem(models.Model):
    class Meta:
        verbose_name = u'Элемент каталога'
        verbose_name_plural = u'Элементы каталога'

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=u'Родительский', null=True, blank=True)

    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    short_description = models.TextField(verbose_name=u'Краткое описание', null=True, blank=True)
    description = HTMLField(verbose_name=u'Описание', null=True, blank=True)

    # fields required for SEO
    seo_title = models.CharField(verbose_name=u'SEO заголовок', max_length=200, null=True, blank=True)
    seo_description = models.TextField(verbose_name=u'SEO описание', null=True, blank=True)
    seo_keywords = models.CharField(verbose_name=u'SEO ключевые слова', max_length=200, null=True, blank=True)
    
    # relations
    section = models.OneToOneField('Section', related_name='tree', null=True, blank=True)
    item = models.OneToOneField('Item', related_name='tree', null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('catalog.views.tree', (), {'item_id': self.id, 'slug': self.slug})
    
    def get_type(self):
        try:
            if self.section.is_meta_item:
                return 'metaitem'
            else:
                return 'section'
        except (Section.DoesNotExist, AttributeError):
            try:
                self.item
                return 'item'
            except Item.DoesNotExist:
                return None

    def delete(self, *args, **kwds):
        if self.get_type() == 'item':
            self.item.delete()
        else:
            self.section.delete()
        super(TreeItem, self).delete(*args, **kwds)
    # template security
    delete.alters_data = True
    
    def get_images(self):
        if self.get_type() == 'item':
            images = self.item.images
        else:
            images = self.section.images
        if images.count() == 0:
            return False
        else:
            return images

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

    is_meta_item = models.BooleanField(verbose_name=u'Мета товар', default=False)
    images = generic.GenericRelation(ItemImage)
    
    def has_nested_sections(self):
        return bool(len(self.tree.children.filter(section__isnull=False,
            section__is_meta_item=False)))

    def __unicode__(self):
        return self.tree.name


class Item(models.Model):
    class Meta:
        verbose_name = u"Продукт каталога"
        verbose_name_plural = u'Продукты каталога'

    # Relation options
    relative = models.ManyToManyField(TreeItem, verbose_name=u'Сопутствующие товары',
                                 null=True, blank=True, related_name='relative')
    sections = models.ManyToManyField(Section, related_name='items',
        verbose_name=u'Разделы', blank=True)
    images = generic.GenericRelation(ItemImage)

    # Sale options
    price = models.DecimalField(verbose_name=u'Цена', null=True, blank=True,
        max_digits=12, decimal_places=2)
    identifier = models.CharField(verbose_name=u'Артикул', max_length=50,
        blank=True, default='')
    barcode = models.CharField(verbose_name=u'Штрих-код', max_length=50,
        null=True, editable=False)
    quantity = models.IntegerField(verbose_name=u'Остаток на складе',
        help_text=u'Введите 0 если на складе нет товара',
        null=True, blank=True)
    
    def __unicode__(self):
        return self.tree.name
