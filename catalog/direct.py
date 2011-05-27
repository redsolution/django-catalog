# -*- coding: utf-8 -*-
from catalog.models import TreeItem
from catalog.utils import connected_models
from django.contrib import admin
from django.core import urlresolvers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.serializers import serialize
from django.db.models import loading
from django.utils import simplejson
from extdirect.django import ExtDirectStore
from extdirect.django.decorators import remoting
from extdirect.django.providers import ExtRemotingProvider


provider = ExtRemotingProvider(namespace='Catalog',
    url='/admin/catalog/treeitem/direct/router/', id='catalog_provider')

class CatalogGridStore(ExtDirectStore):

    def __init__(self, *args, **kwds):
        # Force model=TreeItem
        args += (TreeItem,)
        return super(CatalogGridStore, self).__init__(*args, **kwds)

    def query(self, qs=None, **kw):
        paginate = False
        total = None
        order = False

        if kw.has_key(self.start) and kw.has_key(self.limit):
            start = kw.pop(self.start)
            limit = kw.pop(self.limit)
            paginate = True

        if not qs is None:
            # Don't use queryset = qs or self.model.objects
            # because qs could be empty list (evaluate to False)
            # but it's actually an empty queryset that must have precedence
            queryset = qs
        else:
            queryset = self.model.objects

        queryset = queryset.filter(**kw)

        if not paginate:
            objects = queryset
            total = queryset.count()
        else:
            paginator = Paginator(queryset, limit)
            total = paginator.count

            try:
                page = paginator.page(start + 1)
            except (EmptyPage, InvalidPage):
                #out of range, deliver last page of results.
                page = paginator.page(paginator.num_pages)

            objects = page.object_list

        return self.serialize(objects, total)

    def serialize(self, queryset, total=None):
        meta = {
            'root': self.root,
            'total' : self.total
        }
        res = serialize('catalog_extdirect', queryset, meta=meta, extras=self.extras, total=total)
        return res


class Column(object):
    _map = {
        # python type - xtype
        unicode: 'gridcolumn',
        str: 'gridcolumn',
        bool: 'booleancolumn',
        int: 'numbercolumn',
    }

    xtype = 'gridcolumn'
    type = unicode

    def __init__(self, name, model_cls, model_admin_cls, order=0):
        '''
        Creates a column with name and order
        Detect type by instance
        '''
        self.name = name
        self.order = order

        if name == '__str__':
            header_label = admin.util.label_for_field(name, model_cls, model_admin_cls).decode('utf-8')
        else:
            header_label = admin.util.label_for_field(name, model_cls, model_admin_cls)

        self.header = unicode(header_label)
        attr_type = type(admin.util.lookup_field(name, model_cls(), model_admin_cls)[2])

        # detect type
        if attr_type is int:
            self.type = int
            self.xtype = 'numbercolumn'
        elif attr_type is bool:
            self.type = bool
            self.xtype = 'booleancolumn'
        else:
            # default type and xtype
            self.type = unicode
            self.xtype = 'gridcolumn'
    
    def merge(self, new_field):
        '''
        Merge properties with other model field
        If types are similar, don't change them, otherwise convert all to strings.
        Set order to max order of both instances.
        Returns True if types are similar
        '''
        if self.type == new_field.type:
            self.order =  max(self.order, new_field.order)
            return True
        else:
            self.type = unicode
            self.xtype = 'gridcolumn'
            self.order = max(self.order, new_field.order)
            return False
    
    def serialize(self):
        '''Serialize Column object to python dict'''
        serialized = {
            'header': self.header,
            'dataIndex': self.name,
            'name': self.name,
            'xtype': self.xtype,
            'order': self.order,
        }
        return serialized


class ColumnModel(object):
    '''Represents python-ExtJS map of types for grid'''

    def __init__(self, site):
        '''
        Creates column model singletone. 
        Reads data from django models loader and given site registry
        '''
        self.model_cache = loading.cache
        self.admin_registry = site._registry
        self.fields = {}

        for model_cls in connected_models():
            admin_cls = self.admin_registry[model_cls]

            list_display = list(admin_cls.list_display)
            list_display.remove('action_checkbox')

            # Run over all 'list_display' properties and fill columns
            for i, field_name in enumerate(list_display):
                new_field = Column(field_name, model_cls, admin_cls, i)
                if field_name not in self.fields:
                    self.fields[field_name] = new_field
                else:
                    self.fields[field_name].merge(new_field)

    def serialize(self):
        '''Serialize ColumnModel object to list of serialized Columns'''
        serialized = []
        for column in self.fields.itervalues():
            serialized.append(column.serialize())
        return sorted(serialized, key=lambda x: x['order'])


@remoting(provider, action='treeitem', len=1)
def objects(request):
    '''
    Data grid provider
    '''
    data = request.extdirect_post_data[0]

    parent = data.get('parent', 'root')
    if parent == 'root':
        parent = None

    items = CatalogGridStore()
    res = items.query(parent=parent)
    return res

@remoting(provider, action="treeitem", len=1)
def remove_objects(request):
    data = request.extdirect_post_data[0]
    for object_id in data.get('objects'):
        TreeItem.objects.get(id=object_id).delete()
    return True

@remoting(provider, action='treeitem', len=1)
def tree(request):
    '''
    Server-side expand of tree structure implementation
    '''
    node = request.extdirect_post_data[0]
    if node == 'root':
        node = None
    
    children = TreeItem.objects.filter(parent=node)
    data = []
    for item in children:
        data.append({
            'leaf': getattr(item.content_object, 'leaf', False),
            'id': item.id,
            'text': unicode(item.content_object),
        })
    
    return simplejson.dumps(data)

@remoting(provider, action='treeitem', len=1, form_handler=False)
def move_to(request):
    for item in request.extdirect_post_data:
        source   = item.get('source')
        target   = item.get('target')
        
        if item.get('point') == 'below':
            position = 'right'
        elif item.get('point') == 'above':
            position = 'left'
        elif item.get('point') == 'append':
            position = 'last-child'
        
        for src_id in source:
            if src_id == target:
                continue
            if target == 'root':
                TreeItem.objects.get(id=src_id).move_to(None, position)
            else:
                TreeItem.objects.get(id=src_id).move_to(TreeItem.objects.get(id=target), position)

    return dict(success=True)

@remoting(provider, action='colmodel')
def get_models(request):
    models = []
    for model_cls in connected_models():
        opts = model_cls._meta
        url = urlresolvers.reverse('admin:%s_%s_add' % (opts.app_label, opts.module_name))
        models.append({'app_label': opts.app_label, 'model_name': unicode(opts.verbose_name), 'url': url})
    return models

@remoting(provider, action='colmodel')
def get_col_model(request):
    '''
    Returns JSON configuration which should be passed into 
    ext.grid.ColumnModel() constructor
    '''
    return ColumnModel(admin.site).serialize()

