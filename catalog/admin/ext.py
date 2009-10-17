# -*- coding: utf-8 -*-
import re

from django.http import HttpResponse, HttpResponseServerError, Http404
from django.db import transaction
from django.db import models
from django.contrib.auth.decorators import permission_required
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.sites import AlreadyRegistered

from catalog.models import Section, Item, TreeItem
from catalog.admin.utils import get_grid_for_model, get_tree_for_model
from catalog.utils import render_to

TYPE_MAP = {
    models.AutoField: 'int',
    models.BooleanField: 'boolean',
    models.CharField: 'string',
    models.DateField: 'date',
    models.DateTimeField: 'date',
    models.DecimalField: 'string',
    models.EmailField: 'string',
    models.FileField: 'string',
    models.FloatField: 'float',
    models.IntegerField: 'int',
    models.IPAddressField: 'string',
    models.NullBooleanField: 'boolean',
    models.TimeField: 'date',
    models.SlugField: 'string',
}


class BaseExtAdmin(object):
    '''
    Base class to register model in ext catalog admin
    ..Attributes:
            tree_text_attr - attribute, which will represent object in tree, 
                            othwerwords, text property
            tree_leaf      - is object tree leaf or not, False by default
            tree_hide      - maybe you don't want show objects in tree at all. Use this attribute
            
            fields         - list of fields, which appears in grid. Grid will contains
                             summary fields of all registered models
            m2ms           - enables django-catalog many-to-many stuff for this relations
                             relations may be direct or inverse
            
    '''
    tree_text_attr = 'name'
    tree_leaf = False
    tree_hide = False

    fields = ()
    m2ms = ()


class ExtAdminSite(object):
    # dictionaty with registered models
    _registry = {}
    _m2ms = {}
    chunks = {}
    

    def __init__(self):
        self._urlconf = (
            (r'^json/tree/$', self.tree),
            (r'^json/list/$', self.grid),
            (r'^json/move/$', self.move_node),
            (r'^json/delete_count/$', self.delete_count),
            (r'^json/delete/$', self.delete_items),
            # related stuff
            (r'^rel/json/([\w-]+)/add/$', self.add_related),
            (r'^rel/([\w-]+)/(\d+)/$', self.edit_related),
            (r'^rel/json/([\w-]+)/(\d+)/tree/$', self.tree_related),
            (r'^rel/json/([\w-]+)/(\d+)/save/$', self.save_related),
            # render javascripts
            (r'^catalog.js$', self.config_js),
            (r'^rel/([\w-]+)/(\d+)\.js$', self.config_rel_js),
        )

    def get_registry(self):
        return self._registry

    def get_m2ms(self):
        return self._m2ms

    def register(self, model_class, admin_class):
        '''Register Ext model admin in catalog interface'''
        if model_class not in self._registry:
            self.get_registry().update({model_class: admin_class})
            # register many to many relations specially
            for m2m_field_name in admin_class.m2ms:
                base_field = model_class._meta.get_field_by_name(m2m_field_name)[0]
                # workaround reverse relations
                from django.db.models.related import RelatedObject
                if type(base_field) is RelatedObject:
                    rel_model_class = base_field.model
                else:
                    rel_model_class = base_field.rel.to
                
                m2m_name = '%s-%s-%s' % (model_class.__name__,
                    m2m_field_name, rel_model_class.__name__)

                self._m2ms.update({
                    m2m_name.lower(): {
                        'base_model': model_class,
                        'fk_attr': m2m_field_name,
                        'rel_model': rel_model_class,
                        'url': m2m_name.lower(),
                    }
                })

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

            parent_treeitem = TreeItem.manager.json(parent)
            if parent_treeitem is not None:
                linked_objects = self.get_linked_objects(parent_treeitem.content_object)
                for link in linked_objects:
                    data = get_grid_for_model(link, self.get_registry().get(link.__class__, None))
                    if data is not None:
                        data.update({
                            'type': 'link',
                            'id': '%s-link' % data['id'],
                        })
                        grid.append(data)

        return HttpResponse(simplejson.encode({'items': grid}))

    def move_node(self, request, match):
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

            new_parent = TreeItem.manager.json(target_id)
            move = []
            for source in sources:
                this_section = TreeItem.manager.json(source)
                move.append(may_move(this_section, new_parent))

            if all(move):
                for source in sources:
                    this_section = TreeItem.manager.json(source)
                    this_section.move_to(new_parent, position)
                return HttpResponse('OK')
            else:
                return HttpResponseServerError('Can not move')


    def delete_count(self, request, match):
        try:
            items_list = request.REQUEST.get('items', '').split(',')
            # workaround for empty request
            if u'' in items_list:
                items_list.remove(u'')
            # remove links' id
            items_list = [el for el in items_list if not el.endswith('-link')]
            if len(items_list) > 0:
                items_to_delete = TreeItem.manager.filter(id__in=items_list)
                children_to_delete = 0
                for item in items_to_delete:
                    children_to_delete += item.get_descendant_count()
                return HttpResponse(simplejson.encode({
                    'items': len(items_to_delete),
                    'all': len(items_to_delete) + children_to_delete,
                }))
            else:
                return HttpResponse(simplejson.encode({
                    'items': 0,
                    'all': 0,
                }))
        except (ValueError, TreeItem.DoesNotExist),e:
            return HttpResponseServerError('Bad arguments: %s' % e)

    @transaction.commit_on_success
    def delete_items(self, request, match):
        try:
            items_list = request.REQUEST.get('items', '').split(',')
            parent_id = request.REQUEST.get('parent_id', None)
            parent = TreeItem.manager.json(parent_id)
            # delete objects
            objects_list = [el for el in items_list if not el.endswith('-link')]
            objects_to_delete = TreeItem.objects.filter(id__in=objects_list)
            for item in objects_to_delete:
                for descendant in item.get_descendants():
                    descendant.delete()
                item.delete()

            # delete m2m relations
            linked_treeitem_ids = [el.replace('-link', '') for el in items_list if el.endswith('-link')]
            linked_treeitems = self.get_linked_queryset(
                parent.content_object).filter(id__in=linked_treeitem_ids)
            for treeitem in linked_treeitems:
                self.remove_m2m_object(parent, treeitem)
            
            return HttpResponse('OK')
        except ValueError, TreeItem.DoesNotExist:
            return HttpResponseServerError('Bad arguments')

    #  ---------------------- 
    # | Many to many stuff   |
    #  ---------------------- 

    def _get_m2m(self, match):
        '''utility to retrieve m2m from m2m site registry'''
        m2m = self.get_m2ms().get(match[0], None)
        if m2m is None:
            raise Http404
        return m2m

    def get_linked_objects(self, instance):
        '''
        Returns list of treeitems for objects, linked to instance
        through extAdmin API
        '''
        base_model = instance.__class__
        linked_list = []
        for relation in self.get_m2ms().itervalues():
            if relation['base_model'] == base_model:
                rel_manager = getattr(instance, relation['fk_attr'])
                linked_list += rel_manager.all()
        return linked_list

    def get_linked_queryset(self, instance):
        '''
        Same as get_linked_objects, but returns a queryset with TreeItems
        '''
        base_model = instance.__class__
        tree_ids = []
        for relation in self.get_m2ms().itervalues():
            if relation['base_model'] == base_model:
                rel_manager = getattr(instance, relation['fk_attr'])
                tree_ids += rel_manager.values_list('tree_id', flat=True)
        return TreeItem.objects.filter(id__in=tree_ids)

    def remove_m2m_object(self, parent_treeitem, treeitem):
        def get_m2m_for_two_classes(m2m_list, base_cls, rel_cls):
            result = []
            for m2m in m2m_list: 
                if (m2m['base_model'] is parent_treeitem.content_object.__class__ and
                    m2m['rel_model'] is treeitem.content_object.__class__):
                    result.append(m2m)
            return result

        m2ms = get_m2m_for_two_classes(self.get_m2ms().itervalues(),
            parent_treeitem.content_object.__class__, treeitem.content_object.__class__)
        for relation in m2ms:
            rel_manager = getattr(parent_treeitem.content_object, relation['fk_attr'])
            rel_manager.remove(treeitem.content_object)
            
    def add_related(self, request, match):
        m2m = self._get_m2m(match) 

        instance_id = request.REQUEST.get('target', None)
        instance = get_object_or_404(m2m['base_model'], tree_id=instance_id)
        
        rel_list = request.REQUEST.get('source', u'').split(',')
        related_manager = getattr(instance, m2m['fk_attr'])
        # workaround for empty request
        if u'' in rel_list:
            rel_list.remove(u'')

        for rel_obj_id in rel_list:
            rel_obj = get_object_or_404(m2m['rel_model'], tree_id=rel_obj_id)
            related_manager.add(rel_obj)
        
        return HttpResponse('OK')

    def edit_related(self, request, match):
        m2m = self._get_m2m(match)
        obj_id = match[1]
        context_data = {
            'verbose_name': m2m['base_model']._meta.verbose_name,
            'instance': get_object_or_404(m2m['base_model'], tree_id=obj_id),
            'm2m': m2m,
        }

        return render_to_response('admin/catalog/edit_related.html', context_data)


    def save_related(self, request, match):
        m2m = self._get_m2m(match) 

        instance_id = match[1] 
        instance = get_object_or_404(m2m['base_model'], tree_id=instance_id)
        
        rel_list = request.REQUEST.get('items', u'').split(',')
        related_manager = getattr(instance, m2m['fk_attr'])
        # workaround for empty request
        if u'' in rel_list:
            rel_list.remove(u'')

        # add new and items
        ids_to_add = [obj_id for obj_id in rel_list
            if int(obj_id) not in related_manager.values_list('tree_id', flat=True)]
        # remove deselected
        objs_to_remove = [obj for obj in related_manager.all()
            if str(obj.tree_id) not in rel_list]

        for new_obj_id in ids_to_add:
            new_obj = get_object_or_404(m2m['rel_model'], tree_id=new_obj_id)
            related_manager.add(new_obj)

        for obj in objs_to_remove:
            related_manager.remove(obj)

        return HttpResponse('OK')

    def tree_related(self, request, match):
        # m2m tree editor for RelatedField
        m2m = self._get_m2m(match)
        if m2m is None:
            raise Http404
        obj_id = match[1]

        instance = get_object_or_404(m2m['base_model'], tree_id=obj_id)
        related_manager = getattr(instance, m2m['fk_attr'])

        tree = []
        if request.method == 'POST':
            parent = request.REQUEST.get('node', 'root')

            for treeitem in TreeItem.manager.json_children(parent):
                data = get_tree_for_model(treeitem.content_object,
                    self._registry.get(treeitem.content_object.__class__, None))
                
                # add checkboxes where they can be placed
                if treeitem.content_type.model == m2m['rel_model'].__name__.lower():
                    data.update({
                        'checked': treeitem.content_object.id in related_manager.values_list('id', flat=True),
                    })
                tree.append(data)
        return HttpResponse(simplejson.encode(tree), mimetype='text/json')

    def config_js(self, request, match):
        '''Render ExtJS interface'''
        context_data = {'models': []}
        column_model = {}
        relations = {}

        for model_cls, admin_cls in self.get_registry().iteritems():
            context_data['models'].append(
                {
                    'name': model_cls.__name__.lower(),
                    'verbose_name': model_cls._meta.verbose_name,
                }
            )
            #retrieve column model from classes
            for field in admin_cls.fields:
                field_cls = model_cls._meta.get_field_by_name(field)[0]
                column_model.update({
                    field: {
                        'name': field,
                        'type': TYPE_MAP[type(field_cls)],
                        'header': field_cls.verbose_name,
                    #TODO: add more functional here
                    }
                })
            for m2m_name, m2m in self.get_m2ms().iteritems():
                relations.update({
                    m2m_name: {
                        'menu_name': m2m['rel_model']._meta.verbose_name,
                        'menu_name_plural': m2m['rel_model']._meta.verbose_name_plural,
                        'url': m2m_name,
                        'target': m2m['base_model'].__name__.lower(),
                        'source': m2m['rel_model'].__name__.lower(),
                    }
                })

            context_data['column_model'] = column_model
            context_data['relations'] = relations
            context_data['chunks'] = self.chunks

        return render_to_response('admin/catalog/catalog.js', context_data, mimetype='text/javascript')

    def config_rel_js(self, request, match):
        '''Render relation editor js'''
        m2m = self._get_m2m(match)
        tree_id = match[1]
        instance = get_object_or_404(m2m['base_model'], tree_id=tree_id)
        context_data = {
            'm2m': m2m,
            'instance': instance,
            'rel_verbose_name': m2m['rel_model']._meta.verbose_name,
            'rel_verbose_name_plural': m2m['rel_model']._meta.verbose_name_plural,
        }

        return render_to_response('admin/catalog/edit_related.js', context_data, mimetype='text/javascript')

ext_site = ExtAdminSite()

