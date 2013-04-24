# -*- coding: utf-8 -*-
from catalog.utils import connected_models, get_q_filters, query_set_manager
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel


class TreeItemQuerySet(models.query.QuerySet):

    def published(self):
        tree_q = Q()

        for model_cls, model_filter in get_q_filters().iteritems():
            ct = ContentType.objects.get_for_model(model_cls)
            if model_filter is not None:
                object_ids = model_cls.objects.filter(model_filter).values_list('id', flat=True)
                tree_q |= Q(object_id__in=object_ids, content_type=ct)
            else:
                tree_q |= Q(content_type=ct)

        return self.filter(tree_q)

    def for_model(self, model_class):
        content_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type=content_type)


class TreeItem(MPTTModel):
    """
    Generic model for handle tree organization.
    It can organize different objects into tree without
    modification 3rd party tables. 
    """

    class Meta:
        verbose_name = _('Catalog tree item')
        verbose_name_plural = _('Manage catalog')
        ordering = ['tree_id', 'lft']

    parent = models.ForeignKey(
        'self', related_name='children',
        verbose_name=_('Parent node'), null=True, blank=True, editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    objects = query_set_manager(TreeItemQuerySet)

    def __unicode__(self):
        return unicode(self.content_object)

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def delete(self, *args, **kwargs):
        for child in self.get_children():
            child.delete()
        self.content_object.delete()
        super(TreeItem, self).delete(*args, **kwargs)
    delete.alters_data = True


def insert_in_tree(sender, instance, **kwargs):
    """
    Insert newly created object in catalog tree.
    If no parent provided, insert object in tree root 
    """
    # to avoid recursion save, process only for new instances
    created = kwargs.pop('created', False)

    if created:
        parent = getattr(instance, 'parent', None)
        if parent is None:
            tree_item = TreeItem(parent=None, content_object=instance)
        else:
            tree_item = TreeItem(parent=parent, content_object=instance)
        tree_item.save()


for model_cls in connected_models():
    # set post_save signals on connected objects:
    # for each connected model connect 
    # automatic TreeItem creation for catalog models
    post_save.connect(insert_in_tree, model_cls)
