# -*- conding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from catalog.models import TreeItem
from catalog.utils import render_to
from catalog import settings as catalog_settings


@render_to('catalog/treeitem.html')
def tree(request, item_id=None, slug=None, model=None):
    '''TreeItem view, slug in url ignored'''
    # root page condition
    if not (item_id or slug or model):
        if catalog_settings.CATALOG_ROOT_PAGE:
            try:
                treeitem = TreeItem.objects.all()[0]
            except IndexError:
                raise Http404
        else:
            raise Http404
    elif catalog_settings.CATALOG_URL_SCHEME in ['id', 'combo']:
        treeitem = get_object_or_404(TreeItem, id=item_id)
    elif catalog_settings.CATALOG_URL_SCHEME == 'slug':
        ModelClass = get_object_or_404(ContentType, model=model).model_class()
        instance = get_object_or_404(ModelClass, slug=slug)
        treeitem = instance.tree.get()

    children = treeitem.all_children().all()
    siblibgs = treeitem.all_siblings().all()

    return {
        'treeitem': treeitem,
        'children': children,
        'siblibgs': siblibgs,
    }
