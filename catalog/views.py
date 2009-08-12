from django.shortcuts import get_object_or_404
from catalog.models import TreeItem
from django.db.models import Q
from django.http import Http404
from utils.decorators import render_to


def tree(request, item_id, slug=None):
    '''TreeItem view, slug in url ignored'''
    treeitem = get_object_or_404(TreeItem, pk=item_id)
    #TODO: Add type filter
    return {
        'treeitem': treeitem,
        'children': treeitem.children().all(), 
    }

@render_to('catalog/section.html')
def section(request, tree_item):
    section = tree_item.section
    sub_sections = [item.section for item in 
        tree_item.children.filter(show=True, section__isnull=False)]
    metaitems = [item.section for item in 
        tree_item.children.filter(show=True, section__isnull=False, 
        section__is_meta_item=True)]
    items = tree_item.children.filter(Q(show=True, item__isnull=False) | 
            Q(show=True, section__is_meta_item=True))
    return {
        'tree_item': tree_item,
        'section': section,
        'subsections': sub_sections,
        'items': items,
        'metaitems': metaitems,
    }

@render_to('catalog/metaitem.html')
def metaitem(request, tree_item):
    section = tree_item.section
    items = [tree_item.item for tree_item in
        tree_item.children.filter(show=True, item__isnull=False)]
    return {
        'tree_item': tree_item,
        'section': section,
        'items': items,
        'images': section.images.all(),
    }

@render_to('catalog/item.html')
def item(request, tree_item):
    item = tree_item.item
    return {
        'tree_item': tree_item,
        'item': item,
        'relative': item.relative.all(),
        'images': item.images.all(),
    }
