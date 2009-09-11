# -*- coding: utf-8 -*-

from django.db import models
from tinymce.models import HTMLField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from catalog.fields import RelatedField
from catalog import settings as catalog_settings
from imagekit.models import ImageModel

if catalog_settings.USE_MPTT:
    from mptt import register, AlreadyRegistered
else:
    from catalog.dummy_mptt import register, AlreadyRegistered

from django.core.exceptions import ObjectDoesNotExist,ImproperlyConfigured


class TreeItemManager(models.Manager):

    def json(self, parent):
        if parent == 'root':
            parent = None
            
        return TreeItem.objects.filter(parent=parent)

    def linked(self, treeid):
        if treeid == 'root':
            return []
        treeitem = TreeItem.objects.get(id=treeid)
        if treeitem.content_type.model == 'section':
            related_ids = treeitem.content_object.items.values_list('id', flat=True)
            item_ct = ContentType.objects.get_for_model(Item)
            related = TreeItem.objects.filter(content_type=item_ct, object_id__in=related_ids)
            return related 

class TreeItem(models.Model):
    class Meta:
        verbose_name = u'Элемент каталога'
        verbose_name_plural = u'Элементы каталога'
        if catalog_settings.USE_MPTT:
            ordering = ['tree_id', 'lft']
        else:
            ordering = ['id']

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=u'Родительский', null=True, blank=True, editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    manager = TreeItemManager()

    @models.permalink
    def get_absolute_url(self):
        return self.get_absolute_url_undecorated()

    def get_level(self):
        ''' need to override this, because when we turn mptt off,
            level attr will clash with level method
        '''
        return self.level

    def get_absolute_url_undecorated(self):
        return ('catalog.views.tree', (), {'item_id': self.id, 'slug': self.slug()})
    
    def slug(self):
        try:
            return self.content_object.slug
        except:
            return u'slug'

try:
    register(TreeItem, tree_manager_attr='objects')
except AlreadyRegistered:
    pass


def itemname(value):
    value = value.replace('.', '. ')
    parts = value.split("'")
    if len(parts) < 2:
        parts = value.split('|')
    if len(parts) > 1:
        name = parts[1]
    else:
        name = value
    return name.strip()

class Section(models.Model):
    class Meta:
        verbose_name = u"Раздел каталога"
        verbose_name_plural = u'Разделы каталога'

    tree = generic.GenericRelation(TreeItem)
    images = generic.GenericRelation('TreeItemImage')
    
    # Display options
    show = models.BooleanField(verbose_name=u'Отображать', default=True)

    # Primary options
    slug = models.SlugField(verbose_name=u'Slug', max_length=200, null=True, blank=True)
    name = models.CharField(verbose_name=u'Наименование', max_length=200, default='')
    short_description = models.TextField(verbose_name=u'Краткое описание', null=True, blank=True)
    description = models.TextField(verbose_name=u'Описание', null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return self.tree.get().get_absolute_url()

    def formatted_name(self):
        return itemname(self.name)
    
    def get_all_items(self):
        children = self.tree.get().children_item() | self.tree.get().children_metaitem()
        related_ids = self.items.values_list('id', flat=True)
        item_ct = ContentType.objects.get_for_model(Item)
        metaitem_ct = ContentType.objects.get_for_model(MetaItem)
        related_items = TreeItem.objects.filter(content_type=item_ct, object_id__in=related_ids)
        related_metaitems = TreeItem.objects.filter(content_type=metaitem_ct, object_id__in=related_ids)
        return children | related_items | related_metaitems

    def get_all_items_show(self):
        filtered = []
        for treeitem in self.get_all_items():
            if treeitem.content_object.show:
                filtered.append(treeitem)
        return filtered

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
            'type': self.tree.get().content_type.model, 
            'itemid': self.id,
            'show': self.show,
            'price': 0.0, 
            'quantity': 0, 
            'has_image': bool(self.images.count()),
            'has_description': bool(self.description),
        }
    
    def has_nested_sections(self):
        section_ct = ContentType.objects.get_for_model(Section)
        return bool(len(self.tree.get().children.filter(content_type=section_ct)))

    def __unicode__(self):
        return self.name


class MetaItem(Section):
    class Meta:
        verbose_name = u"Метатовар"
        verbose_name_plural = u'Метатовары'

    tree = generic.GenericRelation(TreeItem)
    images = generic.GenericRelation('TreeItemImage')
    
    @models.permalink
    def get_absolute_url(self):
        return self.tree.get().get_absolute_url_undecorated()
    
    def palletes(self):
        palletes = []
        for child in self.tree.get().children.all():
            palletes += child.content_object.images.filter(pallete=True)
        return palletes

    def price(self):
        return min([child.content_object.price for child in self.tree.get().children.all()])
    

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
    wholesale_price = models.DecimalField(verbose_name=u'Оптовая цена', null=True, blank=True, max_digits=12, decimal_places=2)
    identifier = models.CharField(verbose_name=u'Артикул', max_length=50, blank=True, default='')
    barcode = models.CharField(verbose_name=u'Штрих-код', max_length=50, null=True)
    quantity = models.IntegerField(verbose_name=u'Остаток на складе',
        help_text=u'Введите 0 если на складе нет товара', null=True, blank=True)

    
    @models.permalink
    def get_absolute_url(self):
        return self.tree.get().get_absolute_url_undecorated()
    
    def formatted_name(self):
        return itemname(self.name)

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
            'has_image': bool(self.images.count()),
            'has_description': bool(self.description),
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
        cache_dir = 'upload/catalog/cache'
        spec_module = 'catalog.ikspec'

    def __unicode__(self):
        return self.image.url

# must be at bottom, otherwies breaks imports
from catalog.admin.utils import get_connected_models

def filtered_children_factory(children_ct):
    def func(self):
        return self.children.filter(content_type=children_ct)
    return func
 
for model_cls, admin_cls in get_connected_models():
    content_type = ContentType.objects.get_for_model(model_cls)
    setattr(TreeItem, 'children_%s' % content_type.model, filtered_children_factory(content_type))
