# -*- coding: utf-8 -*-
from catalog import settings as catalog_settings
from catalog.utils import connected_models, get_q_filters
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import Q, loading
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel


class TreeItemManager(models.Manager):

    def published(self):
        tree_q = Q()

        for model_cls, model_filter in get_q_filters().iteritems():
            ct = ContentType.objects.get_for_model(model_cls)
            if model_filter is not None:
                object_ids = model_cls.objects.filter(model_filter).values_list('id', flat=True)
                tree_q |= Q(object_id__in=object_ids, content_type=ct)
            else:
                tree_q |= Q(content_type=ct)

        return self.get_query_set().filter(tree_q)

class TreeItem(MPTTModel):
    '''
    Generic model for handle tree organization.
    It can organize different objects into tree without
    modification 3rd party tables. 
    '''

    class Meta:
        verbose_name = _('Catalog tree item')
        verbose_name_plural = _('Manage catalog')
        ordering = ['tree_id', 'lft']

    parent = models.ForeignKey('self', related_name='children',
        verbose_name=_('Parent node'), null=True, blank=True, editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    objects = TreeItemManager()

    def __unicode__(self):
        return unicode(self.content_object)

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def delete(self, *args, **kwds):
        self.content_object.delete()
        super(TreeItem, self).delete(*args, **kwds)
    delete.alters_data = True


def insert_in_tree(sender, instance, **kwrgs):
    '''
    Insert newly created object in catalog tree.
    If no parent provided, insert object in tree root 
    '''
    # to avoid recursion save, process only for new instances
    created = kwrgs.pop('created', False)

    if created:
        parent = getattr(instance, 'parent', None)
        if parent is None:
            tree_item = TreeItem(parent=None, content_object=instance)
        else:
            tree_item = TreeItem(parent=parent, content_object=instance)
        tree_item.save()
        instance.save()

for model_cls in connected_models():
    if model_cls is None:
        import warnings
        warnings.warn('Can not import model %s from app %s, check CATALOG_MODELS setting, **YOU MAY LOSE DATA!**' % (model_cls.__name__, model_cls._meta.app_label))
    # set post_save signals on connected objects:
    # for each connected model connect 
    # automatic TreeItem creation for catalog models
    post_save.connect(insert_in_tree, model_cls)
