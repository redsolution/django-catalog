from django.shortcuts import get_object_or_404
from catalog.decorators import render_to


@render_to('catalog/treeitem.html')
def tree(request, item_id, slug=None):
    '''TreeItem view, slug in url ignored'''
    treeitem = get_object_or_404(TreeItem, pk=item_id)
    return locals()
