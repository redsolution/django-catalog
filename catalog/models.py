# -*- coding: utf-8 -*-
from catalog.utils import get_connected_models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel


class TreeItem(MPTTModel):
    '''
    Generic model for handle tree organization.
    It can organize different objects into tree without
    modification 3rd party tables. 
    '''
    
    class Meta:
        verbose_name = _('Catalog tree item')
        verbose_name_plural = _('Catalog tree items')
        ordering = ['tree_id', 'lft']

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=_('Parent node'), null=True, blank=True, editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode(self.content_object)
    
    def delete(self, *args, **kwds):
        self.content_object.delete()
        super(TreeItem, self).delete(*args, **kwds)
    delete.alters_data = True


class Link(models.Model):
    '''
    Link model allows to publish one model several times in
    different places in catalog tree
    '''
    
    class Meta:
        verbose_name = _('Catalog link')
        verbose_name_plural = _('Catalog links')
    
    tree = generic.GenericRelation('TreeItem')
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return _('Link to %s') % unicode(self.content_object)

class CatalogBase(models.Model):
    '''
    Base class for inserted in catalog models.
    It contains mixin attributes and methods, that can be useful in your catalog
    '''
    
    class Meta:
        abstract = True
    
    
    tree = generic.GenericRelation('TreeItem')
    links = generic.GenericRelation('Link')
    parent = None  # default parent for objects. See :meth:`~catalog.models.insert_in_tree`


def insert_in_tree(sender, instance, **kwrgs):
    '''
    Insert newly created object in catalog tree.
    If no parent provided, insert object in tree root 
    '''
    # to avoid recursion save, process only for new instances
    created = kwrgs.pop('created', False)

    if created:
        parent = getattr(instance, 'parent')
        if parent is None:
            tree_item = TreeItem(parent=None, content_object=instance)
        else:
            tree_item = TreeItem(parent=parent, content_object=instance)
        tree_item.save()
        instance.save()


for model_cls, admin_cls in get_connected_models():
    # set post_save signals on connected objects:
    # for each connected model connect 
    # automatic TreeItem creation for catalog models
    model_name = model_cls.__name__.lower()
    post_save.connect(insert_in_tree, model_cls)
