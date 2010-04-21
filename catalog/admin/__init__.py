# -*- coding: utf-8 -*-
from django.contrib.admin import site as admin_site
from catalog.admin.utils import get_connected_models
from django.contrib import admin
from django.db.models.signals import class_prepared
from django.http import Http404, HttpResponse
from django.utils.functional import update_wrapper
from django.utils.html import escape

class CatalogAdmin(admin.ModelAdmin):
    '''
    Base admin class to register model as catalog item
    '''
    prepopulated_fields = {'slug': ('name',)}

    # these fields are used in ext_site
    tree_text_attr = 'name'
    tree_leaf = False
    tree_hide = False

    fields = ()
    m2ms = ()

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
                self.instance.parent = request.REQUEST.get('parent', 'root')
                return super(ModelFormCatalogWrapper, self).save(*args, **kwds)

        return ModelFormCatalogWrapper
