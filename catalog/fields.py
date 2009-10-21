from django.db import models
from django import forms
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe


def widget_add_link(add_link):
    def decorator(func):
        def wrapper(*args, **kwds):
            output = [func(*args, **kwds)]
            output.append(u'<a href="%s" class="add-another" id="add_link" onclick="return showAddAnotherPopup(this);"> ' % add_link)
            output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
            return mark_safe(u''.join(output))
        return wrapper
    return decorator

class SelectFromSelected(forms.SelectMultiple):
    '''
    This widget show SelectMultiple admin input with the difference:
    it show only selected options. This may be useful, when you have
    hundreds of options, resulting page loading is too slow.
    ''' 
    
    @widget_add_link('rel')
    def render(self, name, value, attrs=None, choices=[]):
        selected_choices = [(el[0], el[1]) for el in self.choices if el[0] in value]
        self.choices = selected_choices
        return super(SelectFromSelected, self).render(name, value, attrs, choices)

class RelatedField(models.ManyToManyField):
    """
    Catalog related items field 
    """
    def formfield(self, **kwargs):
        kwargs.update({'widget': SelectFromSelected})
        return super(RelatedField, self).formfield(**kwargs)


class MarkItUpField(models.TextField):
    """
    A large string field for markdown content.
    """
    def formfield(self, **kwargs):
        try:
            from markitup.widgets import MarkItUpWidget
        except ImportError:
            from django.forms import Textarea as MarkItUpWidget

        defaults = kwargs.copy()
        defaults.update({'widget': MarkItUpWidget})

        return super(MarkItUpField, self).formfield(**defaults)

