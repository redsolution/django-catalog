# -*- coding: utf-8 -*-
import warnings
from catalog.models import TreeItem
from catalog.utils import get_data_appnames, connected_models, get_q_filters, get_content_objects
from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.helpers import InclusionTag
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import loading
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string

register = template.Library()

TREE_TYPE_EXPANDED = 'expanded'
TREE_TYPE_COLLAPSED = 'collapsed'
TREE_TYPE_DRILLDOWN = 'drilldown'


def get_treeitem_from_context(context, silent=True):
    """
    Utility tries to get TreItem from ``context['object']``.
    
    If silent=False, returns TreeItem instance or raises TemplateSyntaxError,
    otherwise returns TreeItem instance or None
    """
    # Try to resolve ``object`` from context
    if 'object' in context and getattr(context['object'], 'tree', None):
        obj = context['object']
        if hasattr(obj.tree, 'get') and callable(obj.tree.get):
            # Check that object.tree.get() returns TreeItem instance
            if isinstance(context['object'].tree.get(), TreeItem):
                treeitem = obj.tree.get()
                return treeitem
    if silent:
        return None
    else:
        raise TemplateSyntaxError('No TreeItem instance found in context')


class CatalogChildren(Tag):
    """
    Render or get chlidren for given object. Object must be registered in
    catalog tree and have the ``tree.get()`` attribute.

    **Usage**::

        {% catalog_children [for instance] [model 'app_name.model'] [as varname] %}

    **Parameters**:
        for
            Element in tree.
        model
            App label and model name, as they appear in settings.
        var_name
            Name of context variable with result.

    **Magic "for" argument**

        If you specify ``'root'`` as *for* parameter, tag will show you catalog
        root elements.

        If you specify ``'guess'`` as *for* parameter, tag it will try to fetch
        ``object.tree.get()`` from context automatically, and if it find ``TreeItem``
        instance as result of object.tree.get(), it will show children for it.

        Do not worry about call ``catalog_children`` with TreeItem or
        it's content object, *for* argument.
        When tag receive children list, first it will check  if
        ``my_section`` is TreeItem instance, than try to get
        ``my_section.tree.get()`` and raise AttributeError if nothing didn't work.

    **Examples**

        1. Render children tree items for ``my_section`` context object ::

            {% catalog_children for my_section %}

        2. Render children tree items for ``treeitem`` ::

            {% catalog_children for treeitem %}

        3. Render children tree items for ``my_section`` into ``children`` context variable ::

            {% catalog_children for my_section as children %}

        4. Render children tree item with content type ``my_app.Item`` for ``my_section`` ::

            {% catalog_children for my_section model my_app.Item %}

        5. Render all root section tree items ::

            {% catalog_children for 'root' model my_app.Section %}

        6. Render children for ``object`` content object::

            {% catalog_children for 'guess' %}
    """
    name = 'catalog_children'
    templates = ['catalog/children_tag.html', ]

    options = Options(
        'for',
        Argument('instance', required=False),
        'model',
        Argument('model_str', required=False),
        'type',
        Argument('children_type', required=False, resolve=False),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, instance, model_str, children_type, varname):
        if instance == 'root':
            treeitem = None
        elif instance == 'guess':
            treeitem = get_treeitem_from_context(context)
        elif instance is None:
            treeitem = None
        else:
            if isinstance(instance, TreeItem):
                treeitem = instance
            else:
                try:
                    treeitem = instance.tree.get()
                except AttributeError:
                    raise TemplateSyntaxError('Instance argument must have `tree` attribute')

        if children_type:
            warnings.warn(
                "`Type` argument in `catalog_children` is not recommended. "
                "Check for `model` argument and `get_content_objects` filter.")
            ModelClass = None
            for model_cls in connected_models():
                if model_cls._meta.module_name == children_type:
                    ModelClass = model_cls
            if ModelClass is not None:
                model_filter = get_q_filters()[ModelClass]
                if model_filter is not None:
                    queryset = ModelClass.objects.filter(model_filter)
                else:
                    queryset = ModelClass.objects.all()
                allowed_ids = TreeItem.objects.published().filter(
                    parent=treeitem,
                    content_type__model=children_type).values_list(
                        'object_id', flat=True)
                queryset = queryset.filter(id__in=allowed_ids)
            else:
                # Empty
                queryset = []
        else:
            queryset = TreeItem.objects.published().filter(parent=treeitem)

        if model_str:
            model_class = loading.cache.get_model(*model_str.split('.'))
            queryset = queryset.for_model(model_class)

        if varname:
            context[varname] = queryset
            return u''
        else:
            self.templates[0:0] = ['%s/children_tag.html' % app_name for app_name in get_data_appnames()]
            context['children_queryset'] = queryset
            return render_to_string(self.templates, context)

register.tag(CatalogChildren)


def filter_content_objects(treeitems, model_str=None):
    """
    Retrieve content objects for tree items in original order.

    **Usage**::

        {{ tree_items|get_content_objects[:'app_name.model'] }}

    **Parameters**:
        model
            Optional content object model filter.

    **Examples**

        1. Render context object for ``treeitems`` queryset ::

            {% for content_object in treeitems|get_content_objects %}
                {{ content_object }}
            {% endfor %}

        2. Render context object with type my_app.Section for ``treeitems`` queryset ::

            {% for content_object in treeitems|get_content_objects:"my_app.Section" %}
                {{ content_object }}
            {% endfor %}

        3. Render children context object with type my_app.Item for ``my_section`` ::

            {% catalog_children for my_section as children %}
            {% for content_object in children|get_content_objects:"my_app.Item" %}
                {{ content_object }}
            {% endfor %}
    """
    if model_str:
        model_class = loading.cache.get_model(*model_str.split('.'))
    else:
        model_class = None
    return get_content_objects(treeitems, model_class)

register.filter('get_content_objects', filter_content_objects)


class BreadcrumbTag(InclusionTag):
    '''
    TODO: DOCME!
    '''
    name = 'catalog_breadcrumbs'
    template = 'catalog/breadcrumbs.html'

    def get_context(self, context, **kwargs):
        treeitem = get_treeitem_from_context(context, silent=False)
        if treeitem is not None:
            return {
                'breadcrumbs': treeitem.get_ancestors(include_self=True)
            }
        else:
            return {}

register.tag(BreadcrumbTag)


class CatalogTree(Tag):
    """
    Render catalog tree menu.
        
    **Usage**::
    
        {% render_catalog_tree [activate active_treeitem] [model 'app_name.model'] [type 'type'] [current current_treeitem] %}
    
    **Parameters**:
        active_treeitem
            Activate element in tree, highlight or select it.
        model
            App label and model name, as they appear in settings.
        type
            Menu type. Three types available:
            
            * ``drilldown`` - enabled by default. It will expand only active 
                path in tree
            * ``collapsed`` - menu will be collapsed only to dislpay root elements
            * ``expanded`` - all menu nodes will be expanded
        current_treeitem
            Argument for internal usage, for recursion organization.
    
    **Magic "activate" parameter**
    
        By default, ``active_treeitem`` should be ``TreeItem`` instance. But 
        it can accept a several special arguments.
        With {% ... activate 'none' ... %} tag will render tree without 
        active element.
        With {% ... activate 'guess' ... %} tag will try to fetch ``object``
        variable from context, and if success, and if it find
        ``TreeItem`` instance as result of object.tree.get(), it will set
        active_treeitem = object.tree.get() silently.
    
    **Template**
    
        {% render_catalog_tree %} use ``catalog/tree.html`` template to render menu
    
    **Examples**
    
    1. Render full catalog tree ::
       
        {% render_catalog_tree type 'expanded' %}
    
    2. Render drill-down catalog tree ::

        {% render_catalog_tree %}

      same results can be achieved by specifying arguments directly and without *magic*::

        {% render_catalog_tree activate object.tree.get type 'drilldown' %}
    
    3. Render only root nodes for mysection model::
    
        {% render_catalog_tree model 'custom_catalog.mysection' type 'collapsed' %}

    """
    name = 'render_catalog_tree'
    template = 'catalog/tree.html'

    options = Options(
        'activate',
        Argument('active', required=False),
        'model',
        Argument('model_str', required=False),
        'type',
        Argument('tree_type', required=False, default=TREE_TYPE_DRILLDOWN),
        'current',
        Argument('current', required=False),
    )

    def render_tag(self, context, active, model_str, tree_type, current):
        context.push()
        if current is not None:
            children = current.children.published()
        else:
            children = TreeItem.objects.published().filter(parent=None)

        if model_str:
            model_class = loading.cache.get_model(*model_str.split('.'))
            children = children.for_model(model_class)

        if active == 'none':
            active = None
        elif active == 'guess':
            # Try to resolve ``object`` from context
            active = get_treeitem_from_context(context)

        if active is not None:
            context['breadcrumbs'] = [active]
            context['breadcrumbs'].extend(active.get_ancestors())

        context['object_list'] = children
        context['type'] = tree_type
        context['active'] = active
        context['current'] = current

        output = render_to_string(self.template, context)
        context.pop()
        return output

register.tag(CatalogTree)


class GetTreeitem(Tag):
    """
    Returns TreeItem object by content type and slug or by treeitem's id.
    
    **Usage**::
    
        {% get_treeitem [model 'mymodel' slug 'new-one'] [treeid 4] as varname %}
    
    You can get TreeItem by content objects's model name and slug or by ``id`` attribute of the treeitem object.
    
    **Parameters**:
    
    model
        App label and model name, as they appear in settings, for example, ``custom_catalog.mysection``.
    slug
        Content object's slug.
    treeid
        Treeitem's ``id`` attribute. Do not confute is with content object's attribute!
    varname
        Store treeitem object in context variable with this name. If object doesn't found, variable will be ``None``
    
    **Examples**
    
    1. Get catalog section::
    
        {% get_treeitem model 'defaults.section' slug 'catalog' as catalog_treeitem %}
        {% if catalog_treeitem %}
        Chlidren:
            <ul>
            {% for child in catalog_section.children.published %}
                <li>{{ chlid.contento_object.name }}</li>
            {% endfor %}
            </ul>
        {% endif %}
    
    2. Get special treeitem::
    
        {% get_treeitem treeid 4 as special %}
        {% if special %}
            <a href="{{ special.content_object.get_absolute_url }}">{{ special.content_object }}</a>
        {% endif %}
    """
    name = 'get_treeitem'

    options = Options(
        'model',
        Argument('model_str', required=False, resolve=False),
        'slug',
        Argument('slug', required=False),
        'treeid',
        Argument('tree_id', required=False, resolve=False),
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def render_tag(self, context, model_str, slug, tree_id, varname):
        treeitem = None
        if type is not None and slug is not None:
            model_cls = loading.cache.get_model(*model_str.split('.'))
            try:
                content_object = model_cls.objects.get(slug=slug)
                treeitem = content_object.tree.get()
            except ObjectDoesNotExist:
                pass
        elif tree_id is not None:
            try:
                treeitem = TreeItem.objects.get(id=tree_id)
            except ObjectDoesNotExist:
                pass
        context[varname] = treeitem
        return ''

register.tag(GetTreeitem)
