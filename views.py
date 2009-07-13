from django.shortcuts import get_object_or_404
from catalog.models import TreeItem
from django.db.models import Q
from django.http import Http404
from utils.decorators import render_to


def tree(request, item_id, slug=None):
    tree_item = get_object_or_404(TreeItem, pk=item_id)
    if not tree_item.show:
        raise Http404
    item_type = tree_item.get_type()

    if item_type == 'section':
        return section(request, tree_item)
    elif item_type == 'metaitem':
        return metaitem(request, tree_item)
    elif item_type == 'item':
        return item(request, tree_item)
    else:
        raise Http404

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
        'section': section,
        'items': items,
        'images': section.images.all(),
    }

@render_to('catalog/item.html')
def item(request, tree_item):
    item = tree_item.item
    return {
        'item': item,
        'relative': item.relative.all(),
        'images': item.images.all(),
    }
