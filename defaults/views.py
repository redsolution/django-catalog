# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
from catalog.models import TreeItem


def visible(request):
    '''Apply given in request visibility to object in ext admin interface'''
    try:
        treeitems_list = request.REQUEST.get('items', '').split(',')
        show = bool(int(request.REQUEST.get('visible', '1')))
        for treeitem in TreeItem.objects.filter(id__in=treeitems_list):
            treeitem.content_object.show = show
            treeitem.content_object.save()
        return HttpResponse('OK')
    except ValueError:
        return HttpResponseServerError('Bad arguments')
