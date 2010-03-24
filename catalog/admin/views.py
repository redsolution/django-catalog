# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.forms.models import ModelForm, modelformset_factory
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from urllib import urlencode
from catalog.admin.utils import admin_permission_required
from catalog.models import TreeItem


def editor_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    return HttpResponseRedirect('/admin/%s/%s/%s/?%s' %
        (treeitem.content_object.__module__.rsplit('.', 2)[-2], treeitem.content_type.model,
        treeitem.content_object.id, get_str))

def related_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    return HttpResponseRedirect('/admin/catalog/%s/%s/rel/?%s' % (treeitem.content_type.model, treeitem.content_object.id, get_str))

def absolute_url_redirect(request, obj_id):
    treeitem = get_object_or_404(TreeItem, id=obj_id)
    get_str = urlencode(request.GET)
    return HttpResponseRedirect('%s?%s' % (treeitem.content_object.get_absolute_url(), get_str))
