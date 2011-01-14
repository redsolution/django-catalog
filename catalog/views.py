# -*- coding: utf-8 -*-
from catalog.utils import get_connected_models
from catalog.models import TreeItem
from django.views.generic.list_detail import object_detail, object_list


defaults = {
    'template_name': 'catalog/treeitem.html'
}

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
