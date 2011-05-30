# -*- coding: utf-8 -*-
from catalog import settings as catalog_settings
from catalog.models import TreeItem
from catalog.utils import connected_models
from django.db.models import loading
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.views.generic.list_detail import object_detail, object_list

def catalog(request):
    nodes = TreeItem.objects.all()
    return render_to_response('catalog/catalog.html', {'nodes': nodes}, RequestContext(request))

def item_details(request, model, slug):
    models = {}
    for app_label, model_name in catalog_settings.CATALOG_MODELS:
        m = loading.cache.get_model(app_label, model_name)
        models[m.__name__.lower()] = m
    
    ModelClass = models[model]
    object = ModelClass.objects.get(slug=slug)
    item = TreeItem.objects.get(object_id=object.id, content_type__model=model)
    
    return render_to_response('catalog/item.html', {'item': item}, RequestContext(request))

def section_details(request, model, slug):
    models = {}
    for app_label, model_name in catalog_settings.CATALOG_MODELS:
        m = loading.cache.get_model(app_label, model_name)
        models[m.__name__.lower()] = m
    
    ModelClass = models[model]
    object = ModelClass.objects.get(slug=slug)
    node = TreeItem.objects.get(object_id=object.id, content_type__model=model)
    children = node.get_children()
    
    sections = []
    items = []
    for child in children:
        if child.content_object.leaf:
            items.append(child)
        else:
            sections.append(child)

    return render_to_response('catalog/section.html', {'items': items, 'sections': sections, 'cur_node': node}, RequestContext(request))

#===============================================================================
# I will leave onlu these views, all views above should be deleted
#===============================================================================

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
        # select template
        try:
            opts = ModelClass._meta
            t = loader.select_template([
                'catalog/%s/%s.html' % (opts.app_label, opts.module_name),
                'catalog/%s.html' % opts.module_name,
                '%s/%s_in_catalog.html' % (opts.app_label, opts.module_name),
                'catalog/treeitem.html',
            ])
            defaults.update({
                'template_name': t.name,
            })
        except loader.TemplateDoesNotExist:
            pass
        if slug is not None:
            return object_detail(request, ModelClass.objects.all(), slug=slug, **defaults)
        elif id is not None:
            return object_detail(request, ModelClass.objects.all(), object_id=object_id, **defaults)
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
    t = loader.select_template([
        'catalog/%s/%s.html' % (opts.app_label, opts.module_name),
        'catalog/%s.html' % opts.module_name,
        '%s/%s_in_catalog.html' % (opts.app_label, opts.module_name),
    ])
    defaults.update({
        'template_name': t.name,
    })

    return object_list(request, TreeItem.objects.filter(parent=None),
        **defaults)
