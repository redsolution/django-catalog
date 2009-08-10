# -*- coding: utf-8 -*-
from catalog import settings as catalog_settings
from django.contrib import admin
from django.forms import ModelForm
from django.core.urlresolvers import get_mod_func


def import_item(path, error_text):
    u"""Импортирует по указанному пути. В случае ошибки генерируется исключение с указанным текстом"""
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (error_text, path, e))

def get_connected():
    connected_models = []
    for model, modeladmin in catalog_settings.CATALOG_CONNECTED_MODELS:
        model = import_item(model, '')
        modeladmin = import_item(modeladmin, '')
        connected_models.append((model, modeladmin))
    return connected_models

def make_inline_admin(model_class):
    class ModelOptions(admin.StackedInline):
        model = model_class
        fk_name = 'tree'
    return ModelOptions
