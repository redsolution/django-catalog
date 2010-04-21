# -*- coding: utf-8 -*-
from catalog.admin.utils import admin_permission_required, get_grid_for_model, \
    get_tree_for_model, encode_decimal
from catalog.models import TreeItem
from django.contrib.admin.sites import AlreadyRegistered, AdminSite, \
    NotRegistered
from django.db import models, transaction
from django.http import HttpResponse, HttpResponseServerError, Http404, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.utils.functional import update_wrapper
from django.views.generic.simple import direct_to_template
from catalog.admin import CatalogAdmin
from django.db.models.base import ModelBase
from django.utils.http import urlencode


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


class ExtAdminSite(AdminSite):
    # dictionaty with registered models
    _registry = {}
    _m2ms = {}
    chunks = {}

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view, permission=None):
            def wrapper(*args, **kwargs):
                return admin_permission_required(permission)(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            # direct to templates
            url(r'^$', wrap(self.index), name='index'),
            url(r'^closepopup$', wrap(self.closepopup), name='closepopup'),
            # redirects
            url(r'^edit/(\d{1,7})/$',
                wrap(self.editor_redirect, 'catalog.edit_treeitem'),
                name='editor_redirect'),
            url(r'^relations/(\d{1,7})/$',
                wrap(self.related_redirect, 'catalog.edit_treeitem'),
                name='related_redirect'),
            url(r'^view/(\d{1,7})/$',
                wrap(self.absolute_url_redirect),
                name='absolute_url_redirect'),
            # ajax views
            url(r'^json/tree/$', wrap(self.tree), name='catalog_ajax_tree'),
            url(r'^json/list/$', wrap(self.grid), name='catalog_aajx_list'),
            url(r'^json/move/$',
                wrap(self.move_node, 'catalog.edit_treeitem'),
                name='catalog_ajax_move'),
            url(r'^json/delete_count/$', wrap(self.delete_count),
                name='catalog_ajax_delcount'),
            url(r'^json/delete/$',
                wrap(self.delete_items, 'catalog.delete_treeitem'),
                name='catalog_ajax_delete'),
            # related stuff
            url(r'^rel/(?P<m2m_name>[\w-]+)/(?P<obj_id>\d+)/$',
                wrap(self.edit_related, 'catalog.edit_treeitem'),
                name='catalog_m2m_edit'),
            url(r'^rel/json/(?P<m2m_name>[\w-]+)/add/$',
                wrap(self.add_related, 'catalog.add_treeitem'),
                name='catalog_m2m_add'),
            url(r'^rel/json/(?P<m2m_name>[\w-]+)/(?P<obj_id>\d+)/tree/$',
                wrap(self.tree_related),
                name='catalog_m2m_tree'),
            url(r'^rel/json/(?P<m2m_name>[\w-]+)/(?P<obj_id>\d+)/save/$',
                wrap(self.save_related, 'catalog.edit_treeitem'),
                name='catalog_m2m_save'),
            # render javascripts
            url(r'^catalog.js$', wrap(self.config_js),
                name='catalog_js'),
            url(r'^rel/(?P<m2m_name>[\w-]+)/(\d+)\.js$', wrap(self.config_rel_js),
                name='catalog_rel_js'),
        )
        return urlpatterns

    def urls(self):
        return self.get_urls(), self.app_name, self.name
    urls = property(urls)

    def get_registry(self):
        return self._registry

    def get_m2ms(self):
        return self._m2ms

    def register(self, model_or_iterable, admin_class=None, **options):
        '''
        Register Ext model admin in catalog interface, 
        see contrib.admin.site.register
        
        If an admin class isn't given, it will use CatalogAdmin by default
        '''
        if not admin_class:
            admin_class = CatalogAdmin

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]

        for model in model_or_iterable:
            if model in self._registry:
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)
            if options:
                # For reasons I don't quite understand, without a __module__
                # the created class appears to "live" in the wrong place,
                # which causes issues later on.
                options['__module__'] = __name__
                admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)

            self._registry.update({model: admin_class})
            # register many to many relations specially
            for m2m_field_name in admin_class.m2ms:
                base_field = model._meta.get_field_by_name(m2m_field_name)[0]
                # workaround reverse relations
                from django.db.models.related import RelatedObject
                if type(base_field) is RelatedObject:
                    rel_model_class = base_field.model
                else:
                    rel_model_class = base_field.rel.to

                m2m_name = '%s-%s-%s' % (model.__name__,
                    m2m_field_name, rel_model_class.__name__)

                self._m2ms.update({
                    m2m_name.lower(): {
                        'base_model': model,
                        'fk_attr': m2m_field_name,
                        'rel_model': rel_model_class,
                        'url': m2m_name.lower(),
                    }
                })

    def unregister(self, model_or_iterable):
        """
        Unregisters the given model(s).

        If a model isn't already registered, this will raise NotRegistered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]
            # TODO: remove from m2ms

    #===========================================================================
    #  Html views
    #===========================================================================
    def index(self, request):
        '''
        Display base template layout for catalog admin
        '''
        return direct_to_template(request, 'admin/catalog/main.html')

    def closepopup(self, request):
        '''
        Display javascript that closes popup window
        '''
        return direct_to_template(request, 'admin/catalog/closepopup.html')

    def editor_redirect(self, request, obj_id):
        treeitem = get_object_or_404(TreeItem, id=obj_id)
        get_str = urlencode(request.GET)
        # TODO: reverse this url
        return HttpResponseRedirect('/admin/%s/%s/%s/?%s' %
            (treeitem.content_object.__module__.rsplit('.', 2)[-2], treeitem.content_type.model,
            treeitem.content_object.id, get_str))

    def related_redirect(self, request, obj_id):
        treeitem = get_object_or_404(TreeItem, id=obj_id)
        get_str = urlencode(request.GET)
        # TODO: reverse this url
        return HttpResponseRedirect('/admin/catalog/%s/%s/rel/?%s' % (treeitem.content_type.model, treeitem.content_object.id, get_str))

    def absolute_url_redirect(self, request, obj_id):
        treeitem = get_object_or_404(TreeItem, id=obj_id)
        get_str = urlencode(request.GET)
        # TODO: reverse this url
        return HttpResponseRedirect('%s?%s' % (treeitem.get_absolute_url(), get_str))


    #===========================================================================
    #  AJAX views
    #===========================================================================
    def tree(self, request):
        '''Return json encoded tree'''
        tree = []
        if request.method == 'POST':
            parent = request.REQUEST.get('node', 'root')

            for treeitem in TreeItem.manager.json_children(parent):
                data = get_tree_for_model(treeitem.content_object,
                    self._registry.get(treeitem.content_object.__class__))
                if data is not None:
                    tree.append(data)

        return HttpResponse(simplejson.dumps(tree, default=encode_decimal))

    def grid(self, request):
        '''Return json encoded grid data'''
        grid = []
#        if request.method == 'POST':
        if True:
            parent = request.REQUEST.get('node', 'root')

            for treeitem in TreeItem.manager.json_children(parent):
                data = get_grid_for_model(treeitem.content_object,
                    self._registry[treeitem.content_object.__class__])
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

        return HttpResponse(simplejson.dumps({'items': grid}, default=encode_decimal))

    @transaction.commit_on_success
    def move_node(self, request):
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

    def delete_count(self, request):
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
                return HttpResponse(simplejson.dumps({
                    'items': len(items_to_delete),
                    'all': len(items_to_delete) + children_to_delete,
                }))
            else:
                return HttpResponse(simplejson.dumps({
                    'items': 0,
                    'all': 0,
                }))
        except (ValueError, TreeItem.DoesNotExist), e:
            return HttpResponseServerError('Bad arguments: %s' % e)

    @transaction.commit_on_success
    def delete_items(self, request):
        try:
            items_list = request.REQUEST.get('items', '').split(',')
            parent_id = request.REQUEST.get('parent_id', 'root')
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
            if parent:
                linked_treeitems = self.get_linked_queryset(
                    parent.content_object).filter(id__in=linked_treeitem_ids)
                for treeitem in linked_treeitems:
                    self.remove_m2m_object(parent, treeitem)

            return HttpResponse('OK')
        except ValueError, TreeItem.DoesNotExist:
            return HttpResponseServerError('Bad arguments')

    #===========================================================================
    # Many to many internal stuff
    #===========================================================================

    def _get_m2m(self, name):
        '''utility to retrieve m2m from m2m site registry'''
        m2m = self.get_m2ms().get(name, None)
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

    #===========================================================================
    # M2M Html views
    #===========================================================================

    def edit_related(self, request, m2m_name, obj_id):
        m2m = self._get_m2m(m2m_name)
        context_data = {
            'verbose_name': m2m['base_model']._meta.verbose_name,
            'instance': get_object_or_404(m2m['base_model'], tree_id=obj_id),
            'm2m': m2m,
        }

        return render_to_response('admin/catalog/edit_related.html', context_data)

    @transaction.commit_on_success
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


    #===========================================================================
    #  M2M AJAX views
    #===========================================================================
    def tree_related(self, request, m2m_name, obj_id):
        # m2m tree editor for RelatedField
        m2m = self._get_m2m(m2m_name)
        if m2m is None:
            raise Http404

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
        return HttpResponse(simplejson.dumps(tree, default=encode_decimal), mimetype='text/json')


    @transaction.commit_on_success
    def add_related(self, request, m2m_name):
        m2m = self._get_m2m(m2m_name)

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

    @transaction.commit_on_success
    def save_related(self, request, m2m_name, obj_id):
        m2m = self._get_m2m(m2m_name)
        instance = get_object_or_404(m2m['base_model'], tree_id=obj_id)

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

    #===========================================================================
    # render javascript templates 
    #===========================================================================
    def config_js(self, request):
        '''Render ExtJS interface'''
        context_data = {'models': []}
        column_model = {}
        relations = {}

        for model_cls, admin_cls in self.get_registry().iteritems():
            context_data['models'].append(
                {
                    'name': model_cls.__name__.lower(),
                    'verbose_name': model_cls._meta.verbose_name,
                    'app': model_cls.__module__.lower().rsplit('.', 2)[-2],
                }
            )
            #retrieve column model from classes
            for field in admin_cls.catalog_fields:
                try:
                    field_cls = model_cls._meta.get_field_by_name(field)[0]
                except models.FieldDoesNotExist:
                    # get verbose name from function attributes
                    # default type will be string
                    verbose_name = getattr(getattr(model_cls, field), 'verbose_name', u'')
                    field_type = getattr(getattr(model_cls, field), 'type', u'string')
                    field_cls = None
                else:
                    verbose_name = field_cls.verbose_name
                    field_type = 'string'

                column_model.update({
                    field: {
                        'name': field,
                        'type': TYPE_MAP.get(type(field_cls), field_type),
                        'header': verbose_name,
                        'order': admin_cls.catalog_fields.index(field),
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

            context_data['column_model'] = sorted(column_model.itervalues(), key=lambda x: x['order'])
            context_data['relations'] = relations
            context_data['chunks'] = self.chunks

        return render_to_response('admin/catalog/catalog.js', context_data, mimetype='text/javascript')

    def config_rel_js(self, request, m2m_name, obj_id):
        '''Render relation editor js'''
        m2m = self._get_m2m(m2m_name)
        instance = get_object_or_404(m2m['base_model'], tree_id=obj_id)
        context_data = {
            'm2m': m2m,
            'instance': instance,
            'rel_verbose_name': m2m['rel_model']._meta.verbose_name,
            'rel_verbose_name_plural': m2m['rel_model']._meta.verbose_name_plural,
        }

        return render_to_response('admin/catalog/edit_related.js', context_data, mimetype='text/javascript')

catalog_admin_site = ExtAdminSite(name='catalog')
