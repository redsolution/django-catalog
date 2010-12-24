from django.core.urlresolvers import reverse
from django.template import Library


register = Library()

@register.filter(name='admin_url')
def admin_url(object):
    ObjectClass = object.__class__ 
    info = ObjectClass._meta.app_label, ObjectClass._meta.module_name
    return reverse('admin:%s_%s_change' % info, args=[object.id,])
