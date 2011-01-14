# -*- coding: utf-8 -*-
from catalog.models import TreeItem
from catalog.contrib.defaults.models import Item, CatalogImage
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.forms.models import ModelForm
from optparse import make_option
import logging
from time import time
import os
import re


class Command(BaseCommand):
    help = '''
    Import images and descriptions from given directory recursive
    '''
    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=None, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
        make_option('--rewrite-images', default=None, dest='rewrite', type='string',
            help='Should I delete old images, when find new one for instance?'),
    )

    def get_model_form_class(self, model_class):
        class MyModelForm(ModelForm):
            class Meta:
                model = model_class
        return MyModelForm

    def handle(self, *args, **options):
        self.options = options
        start_time = time()

        if self.options['verbose'] == 2:
            logging.getLogger().setLevel(logging.DEBUG)
        elif self.options['verbose'] == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif self.options['verbose'] == 0:
            logging.getLogger().setLevel(logging.ERROR)
        
        if len(args) == 0:
            raise CommandError("You should specify directory to import")
        self.path = args[0]

        self.import_images()

        work_time = time() - start_time
        logging.info('media updated in %s s' % work_time)

    def prepare_upload(self, filename, groups):
        f = open(filename, 'r')
        barcode, suffix, extension = groups
        upload = SimpleUploadedFile('%s%s.%s' % (barcode, suffix, extension), f.read())
        f.close()
        return upload

    def import_images(self):
        logging.info('=== Importing images ===')
        self.regexp = re.compile('^(\d{1,13})(.*)\.(jpg|bmp|png|gif)')
        
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                match = self.regexp.match(filename)
                if match is not None:
                    uploaded_file = self.prepare_upload(
                        os.path.join(root, filename), match.groups())
                    self.upload_image(match.groups(), uploaded_file)
    
    def upload_image(self, groups, uploaded_file):
        try:
            instance = Item.objects.get(article=groups[0])

            if self.options['rewrite']:
                instance.images.all().delete()

            logging.debug('going to update %s with %s ' % (instance, uploaded_file))

            FormClass = self.get_model_form_class(CatalogImage)
            post_data = FormClass(instance=instance).initial
            content_type = ContentType.objects.get_for_model(Item)
            post_data.update({
                'tree_id': instance.id,
                'content_type': content_type.id,
                'object_id': instance.id,
            })

            # see http://docs.djangoproject.com/en/dev/ref/forms/api/#binding-uploaded-files-to-a-form
            file_data = {'image': uploaded_file}
            form = FormClass(post_data, file_data)

            if form.is_valid():
                image = form.save()
        except Item.DoesNotExist:
            pass
        except Exception, e:
            logging.debug('error: %s', e)
