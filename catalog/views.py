# -*- coding: utf-8 -*-
from catalog.utils import get_connected_models
from catalog.models import TreeItem
from django.views.generic.list_detail import object_detail, object_list
from django.db.models import loading
from django.shortcuts import render_to_response
from django.template import RequestContext
from catalog import settings as catalog_settings

defaults = {
    'template_name': 'catalog/treeitem.html'
}

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

def by_id(request, slug, object_id):
    return object_detail(request, TreeItem.objects.all(), object_id=object_id, **defaults)

def by_slug(request, model, slug):
    models = {}
    for model_cls, admin_cls in get_connected_models():
        models[model_cls.__name__.lower()] = model_cls
    ModelClass = models[model]
    return object_detail(request, ModelClass.objects.all(), slug=slug, **defaults)

def root(request):
    return object_list(request, TreeItem.objects.filter(parent=None), 
        template_name='catalog/root.html')
