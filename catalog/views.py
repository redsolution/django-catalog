# -*- conding: utf-8 -*-
from django.shortcuts import get_object_or_404
from catalog.models import TreeItem
from catalog.utils import render_to
from catalog import settings as catalog_settings
from django.contrib.contenttypes.models import ContentType


@render_to('catalog/treeitem.html')
def tree(request, item_id=None, slug=None, model=None):
    '''TreeItem view, slug in url ignored'''
    # root page condition
    if not (item_id or slug or model):
        if catalog_settings.CATALOG_ROOT_PAGE:
            # root page
            children = TreeItem.objects.all_children(parent='root')

            return {
                'treeitem': None,
                'children': children,
                'root_page': True,
            }

    if catalog_settings.CATALOG_URL_SHEME == 'id':
        treeitem = get_object_or_404(TreeItem, id=item_id)
    elif catalog_settings.CATALOG_URL_SHEME == 'slug':
        ModelClass = get_object_or_404(ContentType, model=model).model_class()
        instance = get_object_or_404(ModelClass, slug=slug)
        treeitem = instance.tree.get()

    children = treeitem.all_children().all()
    siblibgs = treeitem.all_siblings().all()

    return {
        'treeitem': treeitem,
        'children': children,
        'siblibgs': siblibgs,
        'root_page': False,
    }
