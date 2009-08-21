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


class TreeItemManager(models.Manager):

    def json(self, parent):
        if parent == 'root':
            parent = None
            
        return TreeItem.objects.filter(parent=parent)
    

class TreeItem(models.Model):
    class Meta:
        verbose_name = u'Элемент каталога'
        verbose_name_plural = u'Элементы каталога'
        ordering = ['tree_id', 'lft']

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=u'Родительский', null=True, blank=True, editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    manager = TreeItemManager()

    @models.permalink
    def get_absolute_url(self):
        return ('catalog.views.tree', (), {'item_id': self.id, 'slug': self.slug()})
    
    def slug(self):
        try:
            return self.content_object.slug
        except:
            return u'slug'

try:
    mptt.register(TreeItem, tree_manager_attr='objects')
except mptt.AlreadyRegistered:
    pass



class Section(models.Model):
    class Meta:
        verbose_name = u"Раздел каталога"
        verbose_name_plural = u'Разделы каталога'

    tree = generic.GenericRelation(TreeItem)
    
    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    short_description = models.TextField(verbose_name=u'Краткое описание', null=True, blank=True)
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)

    def ext_tree(self):
        return {
            'text': self.name,
            'id': '%d' % self.tree.get().id,
            'leaf': False,
            'cls': 'folder',
         }
    
    def ext_grid(self):
        return {
            'name': self.name,
            'id': '%d' % self.tree.get().id,
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
        section_ct = ContentType.objects.get_for_model(Section)
        return bool(len(self.tree.get().children.filter(content_type=section_ct)))

    def min_price(self):
        # FIXME: If children are not Item instances?
        return min([child.item.price for child in self.tree.children.all()])

    def __unicode__(self):
        return self.name


class MetaItem(Section):
    class Meta:
        verbose_name = u"Метатовар"
        verbose_name_plural = u'Метатовары'


class Item(models.Model):
    class Meta:
        verbose_name = u"Продукт каталога"
        verbose_name_plural = u'Продукты каталога'
        
    tree = generic.GenericRelation('TreeItem')
    images = generic.GenericRelation('TreeItemImage')

    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    short_description = models.TextField(verbose_name=u'Краткое описание', null=True, blank=True)
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)

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
            'id': '%d' % self.tree.get().id,
            'leaf': True,
            'cls': 'leaf',
         }
    
    def ext_grid(self):
        return {
            'name': self.name,
            'id': '%d' % self.tree.get().id,
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
    
    pallete = models.BooleanField(default=False, verbose_name=u'Палитра',
        help_text=u'Картинка будет отображаться в полном размере после описания')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


    class IKOptions:
        cache_dir = 'upload/cache'
        # other by default

    def __unicode__(self):
        return self.image.url
