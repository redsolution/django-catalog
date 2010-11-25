# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from catalog import settings as catalog_settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


def import_item(path, error_text):
    """Imports a model by given string. In error case raises ImpoprelyConfigured"""
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (error_text, path, e))

def get_connected_models():
    '''
    Returns list like PAGE_CONNECTED_MODELS, but with imports classes
    and generates default ModelAdmin instead Nones
    '''
    def make_admin_class(model_class):
        class AutoAdmin(admin.ModelAdmin):
            model = model_class
        return AutoAdmin

    model_list = []
    for model_str, admin_str in catalog_settings.CATALOG_CONNECTED_MODELS:
        model_class = import_item(model_str, '')
        if admin_str is not None:
            model_list.append(
                (model_class, import_item(admin_str, ''))
            )
        else:
            model_list.append(
                (model_class, make_admin_class(model_class))
            )
    return model_list


def render_to(template_path):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if output is None:
                output = {}
            if not isinstance(output, dict):
                return output
            return render_to_response(template_path, output,
                context_instance=RequestContext(request))
        return wrapper
    return decorator