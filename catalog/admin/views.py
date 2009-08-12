# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.forms.models import ModelForm, modelformset_factory
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from urllib import urlencode

from catalog.models import Section, Item, TreeItemImage, TreeItem


@permission_required('catalog.add_section', login_url='/admin/')
def catalog_index(request):
    return render_to_response('admin/catalog/main.html',
                              context_instance=RequestContext(request))

@permission_required('catalog.add_section', login_url='/admin/')
def close_popup(request):
    return render_to_response('admin/catalog/closepopup.html',
                              context_instance=RequestContext(request))

@transaction.commit_on_success
@permission_required('catalog.add_item', login_url='/admin/')
def add_item(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)

    new_tree_item = TreeItem(parent=parent_tree_item)
    new_tree_item.save()
    new_item = Item(name=u'Новый товар', tree=new_tree_item)
    new_item.save()
    # save type
    new_tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/treeitem/%d/?_popup=1'
        % new_item.id)

@transaction.commit_on_success
@permission_required('catalog.add_section', login_url='/admin/')
def add_section(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)

    new_tree_item = TreeItem(parent=parent_tree_item)
    new_tree_item.save()
    new_section = Section(
        name=u'Новый раздел', tree=new_tree_item)
    new_section.save()
    # save type
    new_tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/treeitem/%d/?_popup=1'
        % new_section.id)

def edit_related(request, obj_id):
    item = get_object_or_404(Item, id=obj_id)
    
    return render_to_response('admin/catalog/edit_related.html', {'item': item},
        context_instance=RequestContext(request))

def editor_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    if treeitem.get_type() == 'item':
        return HttpResponseRedirect('/admin/catalog/item/%s/?%s' % (treeitem.item.id, get_str))
    else:
        return HttpResponseRedirect('/admin/catalog/section/%s/?%s' % (treeitem.section.id, get_str))

