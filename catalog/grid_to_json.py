# -*- coding: utf-8 -*-
from extdirect.django.serializer import Serializer as ExtSerializer
from StringIO import StringIO
from django.utils.encoding import smart_str, smart_unicode
from django.utils import datetime_safe
from catalog.direct import ColumnModel
from django.contrib import admin
from django.core import urlresolvers


class Serializer(ExtSerializer):
    """Overrides functions defined in extdirect.django.
    Field lookups narrowed to ColumnModel query
    """
    def start_object(self, obj):
        self._current = {}
        self._content_object = obj.content_object
        self._admin_cls = admin.site._registry[type(self._content_object)]

    def handle_field(self, obj, field):
        try:
            value = admin.util.lookup_field(field.name, self._content_object, self._admin_cls)[2]
        except AttributeError:
            value = ''
        self._current[field.name] = smart_unicode(value, strings_only=True)

    def handle_model(self, obj):
        url = urlresolvers.reverse('admin:%s_%s_change' %
            (obj.content_object._meta.app_label, obj.content_object._meta.module_name),
            args=[obj.object_id],
        )
        self._current['url'] = url

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        self.options = options
        self.stream = options.get("stream", StringIO())
        self.meta = options.get('meta', dict(root='records', total='total'))
        self.extras = options.get('extras', [])
        total = options.get("total", queryset.count())
        self.start_serialization(total)

        colmodel = ColumnModel(admin.site)
        fields = colmodel.fields.values()
        for obj in queryset:
            self.start_object(obj)
            for field in fields:
                self.handle_field(obj, field)
            self.handle_model(obj)
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()
