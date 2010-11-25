# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.util import flatten_fieldsets
from django.forms.models import modelform_factory
from django.utils.functional import curry
from models import TreeItem, Link
from forms import LinkInsertionForm
from mptt.admin import MPTTModelAdmin

# TODO: Cancel delete action (we need to call delete() method per-object)
admin.site.register(TreeItem, MPTTModelAdmin)
