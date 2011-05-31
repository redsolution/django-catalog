from classytags.arguments import Argument
from classytags.core import Tag, Options
from django import template
from django.template import loader
from django.template.loader import render_to_string
from catalog.utils import get_data_appnames
from catalog.models import TreeItem

register = template.Library()

class CatalogChildren(Tag):
    '''
    Render or get chlidren for given object. Object must be registered in 
    catalog tree and have the ``tree()`` attribute.
    
    Usage::
    
        {% catalog_children for my_section [type children_type] [as varname] %}
    
    Examples::
    
        {% catalog_children for my_section %}
    
    Render children for ``my_section`` context object. ::

        {% catalog_children for my_section as children %}
    
    Render children for ``my_section`` into ``children`` context variable. ::
    
            {% catalog_children for my_section type item %}
    
    Render children only with type ``item`` for ``my_section``.
    
        
        
    '''
    name = 'catalog_children'
    templates = ['catalog/children_tag.html', ]

    options = Options(
        'for',
        Argument('object'),
        'type',
        Argument('children_type', required=False, resolve=False),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, object, children_type, varname):
        treeitem = object.tree.get()
        children_qs = treeitem.children.published()
        if children_type:
            children_qs = children_qs.filter(content_type__model=children_type)

        if varname:
            context[varname] = children_qs
            return ''
        else:
            self.templates[0:0] = ['%s/children_tag.html' % app_name for app_name in get_data_appnames()]
            context['children_queryset'] = children_qs
            return render_to_string(self.templates, context)

register.tag(CatalogChildren)


@register.inclusion_tag('catalog/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    path = []
    tree = TreeItem.objects.all()
    for item in tree:
        if item == context['object'].tree.get():
            for ancestor in item.get_ancestors():
                path.append(ancestor)
            path.append(item)
    context.update({'breadcrumbs': path})
    return context

