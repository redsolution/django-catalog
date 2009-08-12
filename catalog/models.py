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

from django.core.exceptions import ObjectDoesNotExist,ImproperlyConfigured


def import_item(path, error_text):
    u"""Импортирует по указанному пути. В случае ошибки генерируется исключение с указанным текстом"""
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (error_text, path, e))

def get_connected_models():
    model_list = []
    for model_str, admin_str in catalog_settings.CATALOG_CONNECTED_MODELS:
        model_list.append(import_item(model_str, ''))
    return model_list


class TreeItem(models.Model):
    class Meta:
        verbose_name = u'Элемент каталога'
        verbose_name_plural = u'Элементы каталога'
        ordering = ['tree_id', 'lft']

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=u'Родительский', null=True, blank=True, editable=False)
    # для утилизации запросов к БД сохраним тип
    type = models.CharField(max_length=50, verbose_name=u'Тип данных', null=True, editable=False)

    def _get_one_to_one_models(self):
        one_to_ones = []
        connected = get_connected_models()
        for model in connected:
            tree_field = model._meta.get_field_by_name('tree')[0]
            # check it by the way
            if tree_field.rel.to is not TreeItem:
                raise ImproperlyConfigured('tree attribute must point to TreeItem')
            if isinstance(tree_field, models.OneToOneField):
                one_to_ones.append(model)
        return one_to_ones

    def get_one_to_one_modulenames(self):
        modulenames = []
        for one_to_one in self._get_one_to_one_models():
            modulenames.append(one_to_one.__name__.lower())
        return modulenames

    def set_type(self):
        for one_to_one in self._get_one_to_one_models():
            try:
                tree_data = getattr(self, one_to_one.__name__.lower(), None)
                if (tree_data is not None):
                    if (self.type is None or
                        self.type == one_to_one.__name__.lower()):
                        self.type = one_to_one.__name__.lower()
                    else:
                        raise ValueError('TreeItem has already OneToOne relation')
            except ObjectDoesNotExist:
                pass

    def get_type(self):
        if self.type is None:
            self.set_type()
        return self.type

    def save(self, *args, **kwds):
        # Автоматическое выставление type при сохранении
        self.set_type()
        return super(TreeItem, self).save(*args, **kwds)

    def data(self):
        if self.type is not None:
            return getattr(self, self.type)
        else:
            # TODO: Добавить заглушку
            return None

    @models.permalink
    def get_absolute_url(self):
        return ('catalog.views.tree', (), {'item_id': self.id, 'slug': self.get_slug()})
    
    def get_slug(self):
        return u'slug'

try:
    mptt.register(TreeItem, tree_manager_attr='objects')
except mptt.AlreadyRegistered:
    pass



class Section(models.Model):
    class Meta:
        verbose_name = u"Раздел каталога"
        verbose_name_plural = u'Разделы каталога'

    tree = models.OneToOneField('TreeItem')
    
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

    def ext_tree(self):
        return {
            'text': self.name,
            'id': '%d' % self.tree.id,
            'leaf': False,
            'cls': 'folder',
         }
    
    def ext_grid(self):
        return {
            'name': self.name,
            'id': '%d' % self.tree.id,
            'cls': 'folder',
            'type': 'section',
            'itemid': self.id,
            'show': self.show,
            'price': 0.0, 
            'quantity': 0, 
            #'has_image': False if self.tree.images.count() == 0 else True,
            'has_image': False,
            'has_description': False if self.short_description is None else True,
        }
    
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
        
    tree = models.OneToOneField('TreeItem')

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

    def ext_tree(self):
        return {
            'text': self.name,
            'id': '%d' % self.tree.id,
            'leaf': True,
            'cls': 'leaf',
         }
    
    def ext_grid(self):
        return {
            'name': self.name,
            'id': '%d' % self.tree.id,
            'type': 'item',
            'itemid': self.id,
            'show': self.show,
            'price': float(self.price) if self.price is not None else 0.0,
            'quantity': self.quantity, 
            #'has_image': False if self.tree.images.count() == 0 else True,
            'has_image': False,
            'has_description': False if self.short_description is None else True,
        }
    
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
