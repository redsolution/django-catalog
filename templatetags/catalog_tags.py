from django import template
from catalog.models import Section, TreeItem

register = template.Library()


def get_selected_from_cookies(context):
    if 'request' in context:
        request = context['request']
        cookies = request.COOKIES
        if 'section' in cookies:
            print 'SECTION:', cookies['section']
            return int(cookies['section'])

@register.inclusion_tag('catalog/menu.html', takes_context=True)
def catalog_menu(context, section=None):
    # get last selected catalog branch 
    selected_id = get_selected_from_cookies(context)
    
    if section is None:
        children = [tree_item.section for tree_item in 
            TreeItem.objects.filter(parent__isnull=True, section__isnull=False,
            section__is_meta_item=False)]
    else:
        children = [tree_item.section for tree_item in 
            section.tree.children.filter(section__isnull=False,
            section__is_meta_item=False)]
    return locals()

@register.inclusion_tag('catalog/select.html', takes_context=True)
def catalog_select(context):
    # get last selected catalog branch 
    selected_id = get_selected_from_cookies(context)

    sections = [tree_item.section for tree_item in 
        TreeItem.objects.filter(parent__isnull=True, section__isnull=False)[:2]]
    return locals()


def prepopulated_fields_edit_js(context):
    """
    Creates a list of prepopulated_fields that should render Javascript for
    the prepopulated fields for both the admin form and inlines.
    """
    prepopulated_fields = []
    if context['add'] and 'adminform' in context:
        prepopulated_fields.extend(context['adminform'].prepopulated_fields)
    if 'inline_admin_formsets' in context:
        for inline_admin_formset in context['inline_admin_formsets']:
            for inline_admin_form in inline_admin_formset:
                if inline_admin_form.original is not None:
                    prepopulated_fields.extend(inline_admin_form.prepopulated_fields)
    context.update({'prepopulated_fields': prepopulated_fields})
    return context
prepopulated_fields_edit_js = register.inclusion_tag('admin/prepopulated_fields_js.html', takes_context=True)(prepopulated_fields_edit_js)
