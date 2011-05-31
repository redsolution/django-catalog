# -*- coding: utf-8 -*-
from catalog.models import TreeItem
from catalog.utils import connected_models, get_data_appnames, get_q_filters
from django.http import HttpResponseNotFound
from django.template import loader
from django.views.generic.list_detail import object_detail, object_list


def item_view(request, model, slug=None, object_id=None):
    '''
    Render catalog page for object
    
    Url variables:
        model:
            mdoel name
        slug:
            object's slug
        object_id
            object's id
    
    Required at least one of ``slug`` or ``object_id`` parameters
    
    Templates:
        'catalog/<app_label>/<model_name>.html'
        
        'catalog/<model_name>.html'
        
        '<app_label>/<model_name>_in_catalog.html'
        
        'catalog/treeitem.html',
    
    Context taken from ``object_list`` method from ``django.views.generic.list_detail``:
        object_list
            list of objects
        is_paginated
            are the results paginated?
        results_per_page
            number of objects per page (if paginated)
        has_next
            is there a next page?
        has_previous
            is there a prev page?
        page
            the current page
        next
            the next page
        previous
            the previous page
        pages
            number of pages, total
        hits
            number of objects, total
        last_on_page
            the result number of the last of object in the
            object_list (1-indexed)
        first_on_page
            the result number of the first object in the
            object_list (1-indexed)
        page_range:
            A list of the page numbers (1-indexed).
    
    '''
    ModelClass = None
    for model_cls in connected_models():
        if model_cls._meta.module_name == model:
            ModelClass = model_cls

    if ModelClass is not None:
        model_filter = get_q_filters()[ModelClass] 
        if model_filter is not None:
            model_queryset = ModelClass.objects.filter(model_filter)
        else:
            model_queryset = ModelClass.objects.all()
        # select template
        try:
            opts = ModelClass._meta
            t = loader.select_template([
                'catalog/%s/%s.html' % (opts.app_label, opts.module_name),
                'catalog/%s.html' % opts.module_name,
                '%s/%s_in_catalog.html' % (opts.app_label, opts.module_name),
                'catalog/treeitem.html',
            ])
            extra_context = {
                'template_name': t.name,
            }
        except loader.TemplateDoesNotExist:
            pass
        if slug is not None:
            return object_detail(request, model_queryset, slug=slug, **extra_context)
        elif id is not None:
            return object_detail(request, model_queryset, object_id=object_id, **extra_context)
        else:
            return HttpResponseNotFound(_('No object data specified'))

    else:
        return HttpResponseNotFound(_('Model %s does not registered' % model))

def root(request):
    '''
    Render catalog root page.
    
    Templates:
        ``<app_label>/catalog_root.html``
        
        ``catalog/catalog_root.html``
    
    Parameter ``app_label`` looked up in ``CATALOG_MDOELS`` setting in settings.py
    
    Context taken from ``object_detail`` method from ``django.views.generic.list_detail``:
        object_list:
            list of objects
        is_paginated:
            are the results paginated?
        results_per_page:
            number of objects per page (if paginated)
        has_next:
            is there a next page?
        has_previous:
            is there a prev page?
        page:
            the current page
        next:
            the next page
        previous:
            the previous page
        pages:
            number of pages, total
        hits:
            number of objects, total
        last_on_page:
            the result number of the last of object in the
            object_list (1-indexed)
        first_on_page:
            the result number of the first object in the
            object_list (1-indexed)
        page_range:
            A list of the page numbers (1-indexed).

    '''

    templates_list = ['%s/catalog_root.html' % app_name for app_name in get_data_appnames()]
    templates_list.append('catalog/root.html')
    t = loader.select_template(templates_list)
    extra_context = {
        'template_name': t.name,
    }

    return object_list(request, TreeItem.objects.published().filter(parent=None), **extra_context)
