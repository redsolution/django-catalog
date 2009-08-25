# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseServerError
from django.db import transaction
from catalog.models import Section, Item, TreeItem
from django.contrib.auth.decorators import permission_required
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404


@permission_required('catalog.add_section', login_url='/admin/')
def tree(request):
    tree = []
    if request.method == 'POST':
        parent = request.REQUEST.get('node', 'root')
        
        for treeitem in TreeItem.manager.json(parent):
            tree.append(treeitem.content_object.ext_tree())
    
    return HttpResponse(simplejson.encode(tree))


@permission_required('catalog.change_section', login_url='/admin/')
def list(request):
    grid = []
    if request.method == 'POST':
        parent = request.REQUEST.get('node', 'root')

        for treeitem in TreeItem.manager.json(parent):
            grid.append(treeitem.content_object.ext_grid())

        linked_list = TreeItem.manager.linked(parent)
        if linked_list:
            for linked in linked_list: 
                grid_item = linked.content_object.ext_grid()
                grid_item.update({
                    'type': 'link',
                    'cls': 'link',
                })
                grid.append(grid_item)
    
    return HttpResponse(simplejson.encode({'items': grid}))

# moving tree items

def get_tree_item(node):
    if node == 'root':
        item = None
    else:
        try:
            item = TreeItem.objects.get(id=int(node))
        except TreeItem.DoesNotExist, ValueError:
            item = None
    return item

def may_move(node, parent):
    move_matrix = {
        u'item': [u'section', u'metaitem'],
        u'metaitem': [u'section'],
        u'section': [u'section'],
        }
    if parent is None:
        return True
    elif parent.content_type.model in move_matrix[node.content_type.model]:
        return True
    else:
        return False

@transaction.commit_on_success
def move_node(request):
    if request.method == 'POST':
        sources = request.REQUEST.get('source', '').split(',')
        target_id = int(request.REQUEST.get('target', ''))
        point = request.REQUEST.get('point', '')
        if point == 'above':
            position = 'left'
        elif point == 'below':
            position = 'right'
        else:
            position = 'last-child'

        new_parent = get_tree_item(target_id)
        move = []
        for source in sources:
            this_section = get_tree_item(source)
            if may_move(this_section, new_parent):
                move.append(True)
            else:
                move.append(False)

        if all(move):
            for source in sources:
                this_section = get_tree_item(source)
                this_section.move_to(new_parent, position)
            return HttpResponse('OK')
        else:
            return HttpResponseServerError('Can not move')

def visible(request):
    try:
        treeitems_list = request.REQUEST.get('items', '').split(',')
        show = bool(int(request.REQUEST.get('visible', '1')))
        for treeitem in TreeItem.objects.filter(id__in=treeitems_list):
            treeitem.content_object.show=show
            treeitem.content_object.save()
        return HttpResponse('OK')
    except ValueError:
        return HttpResponseServerError('Bad arguments')

def delete_count(request):
    try:
        items_list = request.REQUEST.get('items', '').split(',')
        items_to_delete = TreeItem.objects.filter(id__in=items_list)
        children_to_delete = 0
        for item in items_to_delete:
            children_to_delete += item.get_descendant_count()
        return HttpResponse(simplejson.encode({
            'items': len(items_to_delete),
            'all': len(items_to_delete) + children_to_delete,
        }))
    except ValueError, TreeItem.DoesNotExist:
        return HttpResponseServerError('Bad arguments')

@transaction.commit_on_success
def delete_items(request):
    try:
        items_list = request.REQUEST.get('items', '').split(',')
        items_to_delete = TreeItem.objects.filter(id__in=items_list)
        for item in items_to_delete:
            for descendant in item.get_descendants():
                descendant.delete()
            item.delete()
        return HttpResponse('OK')
    except ValueError, TreeItem.DoesNotExist:
        return HttpResponseServerError('Bad arguments')

class BaseM2MTree(object):
    '''
    Abstract class to impelement many-to-many tree editor admin view
    '''
    # the model, which involves FK
    base_model = None
    # FK model
    rel_model = None
    fk_attr = None

    @classmethod
    def _get_rel_object(cls, obj_id):
        # we want to override this behavior
        return get_object_or_404(cls.rel_model, tree__id=obj_id)

    @classmethod
    @transaction.commit_on_success
    def save(cls, request, obj_id):
        current_item = get_object_or_404(cls.base_model, id=obj_id)
        relative_list = request.REQUEST.get(cls.fk_attr, u'').split(',')
        related_manager = getattr(current_item, cls.fk_attr)

        # workaround for empty request
        if u'' in relative_list:
            relative_list.remove(u'')
        
        # add
        ids_to_add = [obj_id for obj_id in relative_list 
            if int(obj_id) not in related_manager.values_list('id', flat=True)]
        # remove
        objs_to_remove = [obj for obj in related_manager.all()
            if str(obj.tree.get().id) not in relative_list]
        
        for new_obj_id in ids_to_add:
            object = cls._get_rel_object(new_obj_id)
            related_manager.add(object)
        
        for obj in objs_to_remove:
            related_manager.remove(obj)
        return HttpResponse('OK')

    @classmethod
    def tree(cls, request, obj_id):
        current_item = get_object_or_404(cls.base_model, id=obj_id)
        related_manager = getattr(current_item, cls.fk_attr)
        
        tree = []
        if request.method == 'POST':
            parent = request.REQUEST.get('node', 'root')
            for treeitem in TreeItem.manager.json(parent):
                json = treeitem.content_object.ext_tree()
                if treeitem.content_type.model == cls.rel_model.__name__.lower():
                    json.update({
                        'checked': treeitem.content_object.id in related_manager.values_list('id', flat=True), 
                    })
                tree.append(json)
        return HttpResponse(simplejson.encode(tree))


class RelativeTree(BaseM2MTree):
    base_model = Item
    rel_model = Item
    fk_attr = 'relative'


class SectionsTree(BaseM2MTree):
    base_model = Item
    rel_model = Section
    fk_attr = 'sections'

class ItemsTree(BaseM2MTree):
    base_model = Section
    rel_model = Item
    fk_attr = 'items'
