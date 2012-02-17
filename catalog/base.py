# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic

#This file contains Base Mixin for catalog models
#to avoid cross-import from catalog application like catalog.contrib.defaults
#Do not import catalog.models from here!

class CatalogBase(models.Model):
    '''
    Base class for inserted in catalog models.
    It contains mixin attributes and methods, that can be useful in your catalog
    '''

    class Meta:
        abstract = True


    tree = generic.GenericRelation('catalog.TreeItem')
    parent = None  # default parent for objects. See :meth:`~catalog.models.insert_in_tree`
