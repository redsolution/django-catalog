# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
from catalog.models import TreeItem, Section, Item, TreeItemImage
from catalog.importer import BarcodeTextParser, BarcodeImagesParser
from time import time
from django.forms import ModelForm
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = '''
    Import images and descriptions from given directory recursive
    '''
    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=None, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
        make_option('--rewrite-images', default=None, dest='rewrite', type='string',
            help='Should I delete old images, when find new one for instance?'),
        make_option('--pallete', default=None, dest='pallete', type='string',
            help='Import palletes'),
    )

    def get_model_form_class(self, model_class):
        class MyModelForm(ModelForm):
            class Meta:
                model = model_class
        return MyModelForm

    def handle(self, *args, **options):
        self.options = options
        start_time = time()
        
        
        if len(args) == 0:
            raise CommandError("You should specify directory to import")
        self.path = args[0]

        self.import_descriptions()
        self.import_images()


        work_time = time() - start_time
        if self.options['verbose'] >= 1:
            print 'media updated in %s s' % work_time

    def import_descriptions(self):
        if self.options['verbose'] >= 1:
            print '=== Importing descriptions ==='
        text_parser = BarcodeTextParser(self.path)
        for key, value in text_parser:
            try:
                instance = Item.objects.get(barcode=key)

                if self.options['verbose'] >= 2:
                    print 'going to update', instance, 'with', value[:50].replace('\r\n', ' ')

                FormClass = self.get_model_form_class(Item)
                post_data = FormClass(instance=instance).initial
                post_data.update({'description': value})
                form = FormClass(post_data, instance=instance)

                if form.is_valid():
#                    print 'form valid, saving'
                    instance = form.save()
#                    print 'saved ', instance
#                else:
#                    print 'form is not valid'
#                    print form.errors
            except TreeItem.DoesNotExist:
                pass
            except Exception, e:
                if self.options['verbose'] >= 2:
                    print 'error: %s', e

    def import_images(self):
        if self.options['verbose'] >= 1:
            print '=== Importing images ==='
        image_parser = BarcodeImagesParser(self.path)
        for key, image in image_parser:
            try:
                instance = Item.objects.get(barcode=key)

                if self.options['rewrite']:
                    instance.image_set.all().delete()

                if self.options['verbose'] >= 2:
                    print 'going to update', instance, 'with image', image

                FormClass = self.get_model_form_class(TreeItemImage)
                post_data = FormClass(instance=instance).initial
                content_type = ContentType.objects.get_for_model(Item)
                post_data.update({
                    'tree_id': instance.id,
                    'content_type': content_type.id,
                    'object_id': instance.id,
                })
                if self.options['pallete']:
                    post_data.update({'pallete': True})

                # see http://docs.djangoproject.com/en/dev/ref/forms/api/#binding-uploaded-files-to-a-form
                file_data = {'image': image}
                form = FormClass(post_data, file_data)

                if form.is_valid():
#                    print 'form valid, saving'
                    image = form.save()
#                    print 'saved ', image
#                else:
#                    print 'form is not valid'
#                    print form.errors
            except Item.DoesNotExist:
                pass
            except Exception, e:
                if self.options['verbose'] >= 2:
                    print 'error: %s', e
