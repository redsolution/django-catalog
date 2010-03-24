# -*- coding: utf-8 -*-
from catalog.admin.ext import ext_site, BaseExtAdmin
from catalog.admin.utils import get_connected_models
from catalog.models import TreeItem
from django.contrib import admin
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes import generic
from django.db import models
from django.forms.models import modelform_factory
from django.http import Http404, HttpResponse
from django.utils.functional import curry
from django.utils.html import escape


class CatalogAdminMix(admin.ModelAdmin):
    '''Mixin to make popup edit-object windows close on save'''
    prepopulated_fields = {'slug': ('name',)}

    def response_change(self, request, obj):
        """
        Wrapper around Django ModelAdmin method to provide
        popup close on *edit* item
        """
        if ('_continue' not in request.POST) and ('_popup' in request.POST):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(pk_value), escape(obj))) # escape() calls force_unicode.
        return super(CatalogAdminMix, self).response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Redefines get_form ModelAdmin method to add parent attribute to
        object, but not store it in database. We want to pass it to TreeItem class,
        which connected to pre_save() signal of each catalog model 
        """
        FormClass = super(CatalogAdminMix, self).get_form(request, obj, **kwargs)

        class ModelFormCatalogWrapper(FormClass):
            '''
            Wrapper around ModelForm class due to redefine save method for ModelForm
            '''
            def save(self, *args, **kwds):
                '''Redefined ModelForm method in order to set parent attribute'''
                self.instance.parent = request.REQUEST.get('parent', 'root')
                return super(ModelFormCatalogWrapper, self).save(*args, **kwds)

        return ModelFormCatalogWrapper

# register models
def register(model_class, admin_class, ext_admin_class=BaseExtAdmin):
    # register Django admin model
    class CatalogModelAdmin(admin_class, CatalogAdminMix):
        pass
    try:
        admin.site.register(model_class, CatalogModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass
    # register ext admin
    try:
        ext_site.register(model_class, ext_admin_class)
    except admin.sites.AlreadyRegistered:
        pass
