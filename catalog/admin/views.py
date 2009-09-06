# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.forms.models import ModelForm, modelformset_factory
from django.db import transaction
from django.http import HttpResponseRedirect
from urllib import urlencode
from catalog.admin.utils import admin_permission_required
from catalog.models import Section, Item, TreeItem, MetaItem


@admin_permission_required('catalog.add_section')
def catalog_index(request):
    return render_to_response('admin/catalog/main.html',
                              context_instance=RequestContext(request))

@admin_permission_required('catalog.add_section')
def close_popup(request):
    return render_to_response('admin/catalog/closepopup.html',
                              context_instance=RequestContext(request))

@transaction.commit_on_success
@admin_permission_required('catalog.add_item')
def add_item(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)
    item = Item(name=u'Новый товар')
    item.save()

    tree_item = TreeItem(parent=parent_tree_item, content_object=item)
    tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/item/%d/?_popup=1'
        % item.id)

@transaction.commit_on_success
@admin_permission_required('catalog.add_section')
def add_section(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)
    section = Section(name=u'Новый раздел')
    section.save()

    tree_item = TreeItem(parent=parent_tree_item, content_object=section)
    tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/section/%d/?_popup=1'
        % section.id)

@transaction.commit_on_success
@admin_permission_required('catalog.add_metaitem')
def add_metaitem(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)
    metaitem = MetaItem(name=u'Новый метатовар')
    metaitem.save()

    tree_item = TreeItem(parent=parent_tree_item, content_object=metaitem)
    tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/metaitem/%d/?_popup=1'
        % metaitem.id)

def edit_item_related(request, obj_id):
    item = get_object_or_404(Item, id=obj_id)
    return render_to_response('admin/catalog/edit_item_related.html', {'item': item},
        context_instance=RequestContext(request))

def edit_section_related(request, obj_id):
    section = get_object_or_404(Section, id=obj_id)
    return render_to_response('admin/catalog/edit_section_related.html', {'section': section},
        context_instance=RequestContext(request))


def editor_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    return HttpResponseRedirect('/admin/catalog/%s/%s/?%s' % (treeitem.content_type.model, treeitem.content_object.id, get_str))

def related_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    return HttpResponseRedirect('/admin/catalog/%s/%s/rel/?%s' % (treeitem.content_type.model, treeitem.content_object.id, get_str))

def absolute_url_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    return HttpResponseRedirect('%s?%s' % (treeitem.get_absolute_url(), get_str))

