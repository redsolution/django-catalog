# -*- coding: utf-8 -*-
from catalog.forms import LinkInsertionForm
from catalog.models import Link
from django import template
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from models import Item, Section, CatalogImage

class CatalogImageInline(generic.GenericTabularInline):
    model = CatalogImage
    extra = 1


class LinkInline(generic.GenericTabularInline):
    model = Link
    form = LinkInsertionForm


class CatalogAdmin(admin.ModelAdmin):
    
    def add_link(self, request, object_id):
        '''Show new link creation form'''
        model = self.model
        opts = model._meta
        
        obj = self.get_object(request, unquote(object_id))
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
                name='add-link')
        ) + super(CatalogAdmin, self).get_urls()


class ItemAdmin(admin.ModelAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Item


class SectionAdmin(CatalogAdmin, admin.ModelAdmin):
    inlines = [CatalogImageInline]
    prepopulated_fields = {'slug': ('name',)}
    model = Section
    
    # override to show links
    add_form_template = 'admin/catalog/change_form_with_links.html'
    change_form_template = 'admin/catalog/change_form_with_links.html'
    



admin.site.register(Item, ItemAdmin)
admin.site.register(Section, SectionAdmin)
