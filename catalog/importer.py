# -*- coding: utf-8 -*-
import os
import re
from catalog.models import TreeItem, ItemImage, Item, Section
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ModelForm
from django.contrib.contenttypes.models import ContentType


class DirectoryParser(object):
    '''
    Walk through given directory recursively, search files
    by given template and generate a list of dictionaries
    per template per file extension
    '''
    template = ''
    path = '.'
    data = {}

    def __init__(self, path=None, template=None):
        self.data = {}
        self.pk = ''
        if path is not None:
            self.path = path
        if template is not None:
            self.template = template
        self.regexp = re.compile(self.template)

    def __iter__(self):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                match = self.regexp.match(filename)
                if match is not None:
                    yield self.pk, self.process_match(match.groups(), os.path.join(root, filename))

    def process_match(self, groups, filename):
        '''
            Processes a template match event.
            Supposed to override in child classes,
            should return (key, value) to update model instance
        '''
        self.pk = filename
        return {filename: groups}


class BarcodeTextParser(DirectoryParser):
    template = '^(\d{8,13})(.*)\.txt'

    def prepare_upload(self, filename, groups):
        f = open(filename, 'r')
        content = f.read().decode('cp1251')
        f.close()
        return content

    def process_match(self, groups, filename):
        barcode = groups[0]
        result = self.prepare_upload(filename, groups)
        self.pk = barcode
        if barcode in self.data:
            self.data[barcode].append(result)
        else:
            self.data[barcode] = [result,]
        return result

class BarcodeImagesParser(BarcodeTextParser):
    template = '^(\d{8,13})(.*)\.(jpg|bmp|png|gif)'

    def prepare_upload(self, filename, groups):
        f = open(filename, 'r')
        barcode, suffix, extension = groups
        upload = SimpleUploadedFile('%s%s.%s' % (barcode, suffix, extension), f.read())
        if barcode in self.data:
            self.data[barcode].append(upload)
        else:
            self.data[barcode] = [upload,]
        return upload
