# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.forms.models import ModelForm, modelformset_factory
from catalog.models import Section, Item, ItemImage, TreeItem
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required

@permission_required('catalog.add_section', login_url='/admin/')
def catalog_index(request):
    return render_to_response('admin/catalog/main.html',
                              context_instance=RequestContext(request))

@permission_required('catalog.add_section', login_url='/admin/')
def close_popup(request):
    return render_to_response('admin/catalog/closepopup.html',
                              context_instance=RequestContext(request))

@permission_required('catalog.add_section', login_url='/admin/')
def add_section(request):
    parent_id = request.GET.get('parent', None)
    if parent_id == 'root':
        parent_tree_item = None
    else:
        parent_tree_item = TreeItem.objects.get(id=parent_id)

    new_tree_item = TreeItem(parent=parent_tree_item, name=u'Новый раздел')
    new_tree_item.save()
    new_section = Section()
    new_section.save()
    new_tree_item.section = new_section
    new_tree_item.save()
    
    return HttpResponseRedirect('/admin/catalog/section/%d/?_popup=1'
        % new_section.id)
