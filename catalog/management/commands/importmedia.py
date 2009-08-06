# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
from catalog.models import TreeItem, Section, Item, ItemImage
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
    )

    def handle(self, *args, **options):
        self.options = options
        start_time = time()
        
        def get_model_form_class(model_class):
            class MyModelForm(ModelForm):
                class Meta:
                    model = model_class
            return MyModelForm
        
        if len(args) == 0:
            raise CommandError("You should specify directory to import")
        path = args[0]

        if self.options['verbose'] >= 1:
            print '=== Importing descriptions ==='
        text_parser = BarcodeTextParser(path)
        for key, value in text_parser:
            try:
                instance = TreeItem.objects.get(item__barcode=key)

                if self.options['verbose'] >= 2:
                    print 'going to update', instance, 'with', value[:50].replace('\r\n', ' ')

                FormClass = get_model_form_class(TreeItem)
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

        if self.options['verbose'] >= 1:
            print '=== Importing images ==='
        image_parser = BarcodeImagesParser(path)
        for key, image in image_parser:
            try:
                instance = Item.objects.get(barcode=key)

                if self.options['rewrite']:
                    instance.images.all().delete()

                if self.options['verbose'] >= 2:
                    print 'going to update', instance, 'with image', image

                FormClass = get_model_form_class(ItemImage)

                content_type = ContentType.objects.get_for_model(Item)
                post_data = FormClass(instance=instance).initial
                post_data.update({
                    'content_type': content_type.id,
                    'object_id': instance.id
                    })
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

        work_time = time() - start_time
        if self.options['verbose'] >= 1:
            print 'media updated in %s s' % work_time
