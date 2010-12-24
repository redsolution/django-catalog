# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django import template
from django.utils.encoding import force_unicode
from forms import LinkInsertionForm
from models import TreeItem
from mptt.admin import MPTTModelAdmin
from django.utils.translation import ugettext_lazy as _


class CatalogAdmin(admin.ModelAdmin):
    
    def add_link(self, request, object_id):
        '''Show new link creation form'''
        model = self.model
        opts = model._meta
        
        obj = self.get_object(request, unquote(object_id).rstrip('/newlink'))
        content_type = ContentType.objects.get_for_model(obj)
        
        if request.method == 'POST':
            form = LinkInsertionForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse('<script type="text/javascript">window.close();</script>')
        else:
            form = LinkInsertionForm(initial={
                'object_id': obj.id,
                'content_type': content_type.pk,
            })
         
        fields = form.base_fields.keys()
#        fields.remove('content_type')
#        fields.remove('object_id')
        fieldsets = [(None, {'fields': fields})]
        # TODO: Make render_link_form function
        # TODO: Make response_link_add function
        context = {
            'title': _('Add link to %s') % force_unicode(opts.verbose_name),
            'is_popup': request.REQUEST.has_key('_popup'),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'adminform': helpers.AdminForm(
                form,
                fieldsets,
                {},
                (),
                model_admin=self
            ),
            'errors': helpers.AdminErrorList(form, []),
            'form_url': '.',
            'opts': opts,
            'change': False,
            'save_as': False,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
        }
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response('admin/catalog/link_add_form.html',
            context, context_instance=context_instance)

    def get_urls(self, *args, **kwds):
        from django.conf.urls.defaults import patterns, url
        return patterns('',
            url(r'^(\d+)/newlink/$', self.admin_site.admin_view(self.add_link), 
                name='add_link')
        ) + super(CatalogAdmin, self).get_urls()


# TODO: Remove delete action (we need to call delete() method per-object)
admin.site.register(TreeItem, MPTTModelAdmin)
