# -*- coding: utf-8 -*-
import re

from django.http import HttpResponse, HttpResponseServerError, Http404
from django.db import transaction
from django.contrib.auth.decorators import permission_required
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.sites import AlreadyRegistered

from catalog.models import Section, Item, TreeItem
from catalog.admin.utils import get_grid_for_model, get_tree_for_model
from catalog.utils import render_to


class BaseExtAdmin(object):
    '''Base class to register model in ext catalog admin'''
    tree_text_attr = 'name'
    fields = ()
    m2ms = ()


class ExtAdminSite(object):
    # dictionaty with registered models
    _registry = {}

    def __init__(self):
        self._urlconf = (
            (r'^json/tree/$', self.tree),
            (r'^json/list/$', self.grid),
            (r'^js/$', self.config_js),
        )
    
    def get_registry(self):
        return self._registry
    
    def register(self, model_class, admin_class):
        '''Register Ext model admin in catalog interface'''
        if model_class not in self._registry:
            self._registry.update({model_class: admin_class})
        else:
            raise AlreadyRegistered('Model %s already registered' % model_class.__str__)

    def root(self, request, url):
        '''Handle catalog admin views'''
        for reg, func in self._urlconf:
            match = re.match(reg, url)
            if match is not None:
                return func(request, match.groups())
        raise Http404

    def tree(self, request, match):
        '''Return json encoded tree'''
        tree = []
        if request.method == 'POST':
            parent = request.REQUEST.get('node', 'root')

            for treeitem in TreeItem.manager.json_children(parent):
                data = get_tree_for_model(treeitem.content_object,
                    self._registry.get(treeitem.content_object.__class__, None))
                if data is not None:
                    tree.append(data)

        return HttpResponse(simplejson.encode(tree))

    def grid(self, request, match):
        '''Return json encoded grid data'''
        grid = []
        if request.method == 'POST':
            parent = request.REQUEST.get('node', 'root')

            for treeitem in TreeItem.manager.json_children(parent):
                data = get_grid_for_model(treeitem.content_object,
                    self._registry.get(treeitem.content_object.__class__, None))
                if data is not None:
                    grid.append(data)

#            linked_list = TreeItem.manager.linked(parent)
#            if linked_list:
#                for linked in linked_list:
#                    grid_item = linked.content_object.ext_grid()
#                    grid_item.update({
#                        'type': 'link',
#                        'cls': 'link',
#                    })
#                    grid.append(grid_item)

        return HttpResponse(simplejson.encode({'items': grid}))

    def move_node(request):
        '''Move node above, below or into target node'''
        def may_move(node, parent):
            if parent is None:
                return True
            elif node.content_type.model not in parent.content_object.exclude_children:
                return True
            else:
                return False

        if request.method == 'POST':
            sources = request.REQUEST.get('source', '').split(',')
            target = request.REQUEST.get('target', 'root')
            target_id = target
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
                move.append(may_move(this_section, new_parent))

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

#    @render_to('admin/catalog/catalog.js')
    def config_js(self, request, match):
        '''Render ExtJS interface'''
        context_data = {'models': []}
        for model_cls, admin_cls in self._registry.iteritems():
            context_data['models'].append(
                {
                    'name': model_cls.__name__.lower(),
                    'verbose_name': model_cls._meta.verbose_name,
                }
            )

        return render_to_response('admin/catalog/catalog.js',
            context_data)


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
            for treeitem in TreeItem.manager.json_children(parent):
                json = treeitem.content_object.ext_tree()
                if treeitem.content_type.model == cls.rel_model.__name__.lower():
                    json.update({
                        'checked': treeitem.content_object.id in related_manager.values_list('id', flat=True),
                    })
                tree.append(json)
        return HttpResponse(simplejson.encode(tree))


ext_site = ExtAdminSite()

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

