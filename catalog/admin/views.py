# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.forms.models import ModelForm, modelformset_factory
from catalog.models import Section, Item, ItemImage, TreeItem
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from urllib import urlencode


@permission_required('catalog.add_section', login_url='/admin/')
def catalog_index(request):
    return render_to_response('admin/catalog/main.html',
                              context_instance=RequestContext(request))

@permission_required('catalog.add_section', login_url='/admin/')
def close_popup(request):
    return render_to_response('admin/catalog/closepopup.html',
                              context_instance=RequestContext(request))

@permission_required('catalog.add_item', login_url='/admin/')
def add_item(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)

    new_item = Item()
    new_item.save()
    new_tree_item = TreeItem(parent=parent_tree_item,
        name=u'Новый товар', item=new_item)
    new_tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/item/%d/?_popup=1'
        % new_item.id)

@permission_required('catalog.add_section', login_url='/admin/')
def add_section(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)

    new_section = Section()
    new_section.save()
    new_tree_item = TreeItem(parent=parent_tree_item,
        name=u'Новый раздел', section=new_section)
    new_tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/section/%d/?_popup=1'
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

