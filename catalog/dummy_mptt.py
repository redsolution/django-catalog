# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import FieldDoesNotExist, PositiveIntegerField
# Almost clone of mptt.__init__ file.
# Contains overrides for objects in catalog work properly
 
__all__ = ('register',)

class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model for dummy_mptt more than once.
    """
    pass

registry = []


def get_children(self):
    # cross import avoid
    from catalog.models import TreeItem

    return TreeItem.objects.filter(parent=self.id)

def move_to(self, new_parent, position):
    if position == 'last-child':
        self.parent = new_parent
    else:
        self.parent = new_parent.parent  # same level with 'new_parent'
    self.level = get_level(self)
    self.save()


def get_level(self):
    level = 0
    obj = self
    for i in range(10):
        if obj.parent is None:
            break
        else:
            obj = obj.parent
            level += 1
    return level

def get_descendants(self):
    # cross import avoid
    from catalog.models import TreeItem
    def get_children_id_list(iter, id_list=[]):
        for child in iter:
            if child.children.all().count() > 0:
                id_list.append(child.id)
                get_children_id_list(child.children.all(), id_list)
        return id_list

    children_ids = get_children_id_list(self.children.all(), [self.id])
    if children_ids is None:
        children_ids = []
    return TreeItem.objects.filter(parent__in=children_ids)

def get_descendant_count(self):
    return self.get_descendants().count()

def register(model, tree_manager_attr='tree'):
    """
    Dummy mptt add mptt-like atrributes for models in catalog works properly
    without mptt
    """
    if model in registry:
        raise AlreadyRegistered(
            'The model %s has already been registered.' % model.__name__)
    registry.append(model)

    # create null fields if we will want to use mptt in future
    opts = model._meta
    for attr in ['lft', 'rght', 'tree_id', 'level']:
        try:
            opts.get_field(attr)
        except FieldDoesNotExist:
            PositiveIntegerField(
                db_index=True, null=True, editable=False).contribute_to_class(model, attr)

    # Add tree methods for model instances
    setattr(model, 'get_children', get_children)
    setattr(model, 'get_descendants', get_descendants)
    setattr(model, 'get_descendant_count', get_descendant_count)
    setattr(model, 'move_to', move_to)
    setattr(model, 'level', get_level)

    # Add a default manager
    models.Manager().contribute_to_class(model, tree_manager_attr)
    setattr(model, '_tree_manager', getattr(model, tree_manager_attr))
#    setattr(model, tree_manager_attr, models.Manager())
