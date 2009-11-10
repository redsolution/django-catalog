from django.shortcuts import get_object_or_404
from catalog.models import TreeItem
from catalog.utils import render_to


@render_to('catalog/treeitem.html')
def tree(request, item_id=None, slug=None):
    '''TreeItem view, slug in url ignored'''
    if item_id is not None or slug is not None:
        if item_id is not None:
            treeitem = get_object_or_404(TreeItem, id=item_id)
        elif slug is not None:
            treeitem = get_object_or_404(TreeItem, slug=slug)
        children = treeitem.children.all()
        root_page = False
    else:
        # root page
        treeitem = None
        children = TreeItem.manager.json_children(parent='root')
        root_page =True

    return {
        'treeitem': treeitem,
        'children': children,
        'root_page': root_page,
    }

