# -*- coding: utf-8 -*-
from catalog.direct import provider
from django import template
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.utils.html import escape
from models import TreeItem
from mptt.admin import MPTTModelAdmin
from mptt.forms import MoveNodeForm



def context_admin_helper(admin_instance, request, opts, obj):
    return {
        'root_path': admin_instance.admin_site.root_path,
        'is_popup': request.REQUEST.has_key('_popup'),
        'app_label': opts.app_label,
        'form_url': '.',
        'opts': opts,
        'has_add_permission': admin_instance.has_add_permission(request),
        'has_change_permission': admin_instance.has_change_permission(request, obj),
        'has_delete_permission': admin_instance.has_delete_permission(request, obj),
        'change': False,
        'save_as': False,
        'show_delete': False,
    } 


class CatalogAdmin(admin.ModelAdmin):

    # override to show links
    add_form_template = 'admin/catalog/change_form_with_links.html'
    change_form_template = 'admin/catalog/change_form_with_links.html'

    def response_change(self, request, obj):
        """
        Wrapper around Django ModelAdmin method to provide
        popup close on *edit* item
        """
        if ('_continue' not in request.POST) and ('_popup' in request.POST):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(pk_value), escape(obj))) # escape() calls force_unicode.
        return super(CatalogAdmin, self).response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Redefines get_form ModelAdmin method to add parent attribute to
        object, but not store it in database. We want to pass it to TreeItem class,
        which connected to pre_save() signal of each catalog model 
        """
        FormClass = super(CatalogAdmin, self).get_form(request, obj, **kwargs)

        class ModelFormCatalogWrapper(FormClass):
            '''
            Wrapper around ModelForm class due to redefine save method for ModelForm
            '''
            def save(self, *args, **kwds):
                '''Redefined ModelForm method in order to set parent attribute'''
                if 'parent' in request.REQUEST:
                    if request.REQUEST.get('parent') == 'root':
                        parent = None
                    else:
                        try:
                            parent = TreeItem.objects.get(id=request.REQUEST.get('parent'))
                        except ObjectDoesNotExist:
                            parent = None
                    self.instance.parent = parent
                return super(ModelFormCatalogWrapper, self).save(*args, **kwds)

        return ModelFormCatalogWrapper


class TreeItemAdmin(MPTTModelAdmin):
    change_form_template = 'admin/catalog/change_treeiem.html'
    
    
    def move(self, request, object_id):
        '''Move Treeitem form'''
        model = self.model
        opts = model._meta

        treeitem = self.get_object(request, unquote(object_id).rstrip('/move'))
        if request.method == 'POST':
            form = MoveNodeForm(treeitem, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse('<script type="text/javascript">window.close();</script>')
                return HttpResponseRedirect(
                    reverse('admin:catalog_treeitem_change', args=[treeitem.id,])
                )
        else:
            form = MoveNodeForm(treeitem)

        fields = form.base_fields.keys()
        fieldsets = [
            (None, {'fields': fields}),
        ]
        
        context = context_admin_helper(self, request, opts, treeitem)
        context.update({
            'title': _('Move %s') % force_unicode(opts.verbose_name),
            'adminform': helpers.AdminForm(
                form,
                fieldsets,
                {},
                (),
                model_admin=self,
            ),
            'errors': helpers.AdminErrorList(form, []),
        })
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response('admin/catalog/move_node_form.html',
            context, context_instance=context_instance)
    
    def ext_js_config(self, request, extra_context):
        opts = self.model._meta
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)

        # Remove action checkboxes if there aren't any actions available.
        list_display = list(self.list_display)
        context = {
            'list_display': list_display,
            'options': opts,
            'actions': actions,
        }
        if extra_context:
            context.update(extra_context)
        return direct_to_template(request, 'admin/catalog/extjs_admin.html',
            extra_context=context)
    
    def changelist_view_wrapper(self, request, extra_context=None):
        '''Overrides ``changelist_view`` to enable ``plain`` html view key in GET'''
        if 'plain' in request.GET:
            # small hack, do not consider 'plain' in GET attributes
            copied_get = request.GET.copy()
            copied_get.pop('plain')
            request.GET = copied_get
            return super(TreeItemAdmin, self).changelist_view(request, extra_context)
        else:
            if extra_context is None:
                extra_context = {}
            extra_context.update({
                'opts': self.model._meta,
            })
            return self.ext_js_config(request, extra_context)

    def get_urls(self, *args, **kwds):
        from django.conf.urls.defaults import patterns, url
        
        info = self.model._meta.app_label, self.model._meta.module_name
        return patterns('',
            url(r'^$', self.admin_site.admin_view(self.changelist_view_wrapper),
                name='%s_%s_changelist' % info),
            url(r'^(\d+)/move/$', self.admin_site.admin_view(self.move), 
                name='move_tree_item'),
            url(r'^direct/router/$', self.admin_site.admin_view(provider.router),
                name='catalog_provider_router'),
            url(r'^direct/provider.js$', self.admin_site.admin_view(provider.script),
                name='catalog_provider_script'),
        ) + super(TreeItemAdmin, self).get_urls()


# TODO: Remove delete action (we need to call delete() method per-object)
admin.site.register(TreeItem, TreeItemAdmin)
