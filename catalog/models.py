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
    import mptt
else:
    from catalog import dummy_mptt as mptt

from django.core.exceptions import ObjectDoesNotExist,ImproperlyConfigured


class CatalogBase(models.Model):
    '''Base class contains method to interact with extjs admin'''
    class Meta:
        abstract = True
         
    tree = generic.GenericRelation('TreeItem')
    exclude_children = []

    def get_name(self):
        name = getattr(self, 'name', None)
        title = getattr(self, 'title', None)
        return name or title

    def ext_tree(self):
        return {
            'text': self.get_name(),
            'id': '%d' % self.tree.get().id,
            'leaf': False,
            'cls': 'folder',
         }

    def ext_grid(self):
        return {
            'name': self.get_name(),
            'id': '%d' % self.tree.get().id,
            'type': ContentType.objects.get_for_model(self).model, 
            'itemid': self.id,
        }
 

class TreeItemManager(models.Manager):

    def json_children(self, parent):
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
    mptt.register(TreeItem, tree_manager_attr='objects')
except mptt.AlreadyRegistered:
    pass

# HACK: import models by their names for convenient usage
for model_name, admin_name in catalog_settings.CATALOG_CONNECTED_MODELS:
    module, model = model_name.rsplit('.', 1)
    exec('from %s import %s' % (module, model))

# must be at bottom, otherwise breaks imports
from catalog.admin.utils import get_connected_models

def filtered_children_factory(model_name):
    def func(self):
        return self.children.filter(content_type__model=model_name)
    return func
 
for model_cls, admin_cls in get_connected_models():
    model_name = model_cls.__name__.lower()
    setattr(TreeItem, 'children_%s' % model_name, model_name)

