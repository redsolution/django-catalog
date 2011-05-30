# -*- coding: utf-8 -*-
from catalog.contrib.defaults.models import Section, Item
from catalog.models import TreeItem
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError
from optparse import make_option
from time import time
import csv
import logging
import mptt

try:
    from pinyin.urlify import urlify
except ImportError:
    try:
        from pytils.translit import slugify as urlify
    except ImportError:
        from django.template.defaultfilters import slugify as urlify


class Command(BaseCommand):
    help = '''Import items from CSV format
    Usage: manage.py importcsv wares.txt
    '''
    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=0, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
    )
    
    def kwargs_from_list(self, list, klass):
        '''Make dict from list of args, as they go in csv file'''
        if klass is Item:
            return {
                'article': list[0].decode('utf-8'),
                'name': list[2].decode('utf-8'),
                'price': Decimal(list[3].decode('utf-8')),
                'slug': urlify(list[2].decode('utf-8'),),
            }
        elif klass is Section:
            return {
                'name': list[1].decode('utf-8'),
                'slug': urlify(list[1].decode('utf-8'),),
            }
    
    def handle(self, *args, **options):
        start_time = time()
        self.options = options

        if len(args) == 0:
            raise CommandError("You should specify file to import")
        filename = args[0]
        
        if self.options['verbose'] == 2:
            logging.getLogger().setLevel(logging.DEBUG)
        elif self.options['verbose'] == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif self.options['verbose'] == 0:
            logging.getLogger().setLevel(logging.ERROR)

        class csv_format(csv.Dialect):
            delimiter = ';'
            quotechar = '"'
            doublequote = True
            lineterminator = '\r\n'
            quoting = csv.QUOTE_MINIMAL
            
        # Preparing
        reader = csv.reader(open(filename, 'r'), dialect=csv_format)

        logging.info('Loading objects')
        self.load_objects()

        # Run!
        logging.info('Importing items')
        count = self.make_items(reader)

        work_time = time() - start_time
        logging.debug('%s items imported in %s s' % (count, work_time))

    def load_objects(self):
        '''Creates in-memory object cache'''
        def load_from_queryset(queryset, key):
            '''Returns dictionary with key: object, with key lookup from objects'''
            class ObjectReader(object):
                '''Yields queryset object to dict with given key lookup from objects'''
                def __init__(self, queryset, key):
                    self.queryset = queryset
                    self.key = key.split('__')
                
                def _attribute_lookup(self, obj, keys):
                    parent_obj = obj
                    
                    for key in keys:
                        attr_obj = getattr(parent_obj, key)
                        parent_obj = attr_obj
                    return attr_obj
            
                def __iter__(self):
                    for obj in self.queryset:
                        yield {self._attribute_lookup(obj, self.key): obj}
    
            reader = ObjectReader(queryset, key)
            data = {}
            for item in reader:
                data.update(item)
            return data

#        # cache indexes setting
        self.cache = {}
        self.cache['section_by_name'] = load_from_queryset(Section.objects.all(), 'name')
        self.cache['item_by_article'] = load_from_queryset(Item.objects.all(), 'article')

    def _get_or_create_section(self, options, parent):
        name = options['name']
        if name in self.cache['section_by_name']:
            return self.cache['section_by_name'][name].tree.get()
        else:
            section = Section(**options)
            section.parent=parent 
            section.save()
    
            self.cache['section_by_name'].update({section.name: section})
            
            logging.debug('[S] === %s ===' % section)
            return section.tree.get()

    def _update_or_create_item(self, options, parent):
        
        if options['article'] in self.cache['item_by_article']:
            item = self.cache['item_by_article'][options['article']]
            # TODO: update item
            for key, value in options.iteritems():
                setattr(item, key, value)
            item.save()
 
            self.cache['item_by_article'].update({item.article: item})
            logging.debug('[U] %s' % options['name'])
            # True if created
            return False
        else:
            item = Item(**options)
            item.parent = parent
            try:
                item.save()
            except IntegrityError:
                from random import randint
                item.slug = item.slug + '%d' % randint(0,9)
                item.save()

            self.cache['item_by_article'].update({item.article: item})
            logging.debug('[S] %s' % item.name)
            # True if created
            return True

    @transaction.commit_on_success
    def make_items(self, reader):
        # before import
        try:
            import_section = Section.objects.get(name=u'Импорт')
            self.parent_import_section = import_section.tree.get()
        except Section.DoesNotExist:
            self.parent_import_section = self._get_or_create_section(
                {'name':u'Импорт'}, None)
        # run!
        count = 0
        for item in reader:
            self.make_item(item)
            count = count + 1
        return count

    def make_item(self, param_list):
        '''
        Makes a new item in catalog
        param_list = [identifier, quantity, '<section_name> <name>']
        '''
        item_options = self.kwargs_from_list(param_list, Item)
        section_options =  self.kwargs_from_list(param_list, Section)
        
        import_section = self._get_or_create_section(section_options, self.parent_import_section)
        return self._update_or_create_item(item_options, import_section)
