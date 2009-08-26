# -*- coding: utf-8 -*-
from sys import argv
from optparse import make_option
from urlify import urlify
from time import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection, models
from catalog.recalculate import recalculate_mptt
from catalog.models import TreeItem, Section, Item
import mptt
import csv
import logging


def mptt_off():
    cursor = connection.cursor()
    cursor.execute('''
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "lft" DROP NOT NULL;
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "rght" DROP NOT NULL;
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "tree_id" DROP NOT NULL;
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "level" DROP NOT NULL;
    ''')
    models.signals.pre_save.disconnect(mptt.signals.pre_save, sender=TreeItem)

def mptt_on():
    logging.info('rebuilding mptt...')
    recalculate_mptt(TreeItem)
    cursor = connection.cursor()
    cursor.execute('''
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "lft" SET NOT NULL;
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "rght" SET NOT NULL;
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "tree_id" SET NOT NULL;
        ALTER TABLE "catalog_treeitem" ALTER COLUMN "level" SET NOT NULL;
    ''')
    models.signals.pre_save.connect(mptt.signals.pre_save, sender=TreeItem)
    

class Command(BaseCommand):
    help = '''Import items from CSV format
    Usage: manage.py importcsv wares.txt
    '''
    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=0, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
    )
    
    
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
        mptt_off()
        logging.info('Importing items')
        count = self.make_items(reader)
        mptt_on()

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
        
        # cache indexes setting
        self.data = {}
        self.data['treeitem_by_id'] = load_from_queryset(TreeItem.objects.all(), 'id')
        self.data['item_by_identifier'] = load_from_queryset(Item.objects.all(), 'identifier')
        self.data['section_by_name'] = load_from_queryset(Section.objects.all(), 'name')

    def _get_or_create_section(self, name, parent):
        if name in self.data['section_by_name']:
            return self.data['section_by_name'][name].tree.get()
        else:
            section = Section(
                name=name, slug = urlify(name)
            )
            section.save()

            section_tree_item  = TreeItem(parent=parent, content_object=section)
            section_tree_item.save()

            self.data['section_by_name'].update({section.name: section})
            
            logging.debug('[S] === %s ===' % section)
            return section_tree_item

    def _update_or_create_item(self, **kwds):
        item_options_list = [
            'price', 'wholesale_price', 'quantity', 'barcode',
            'identifier', 'short_description', 'name', 'slug',
        ]
        item_options = {}
        for k, v in kwds.iteritems():
            if k in item_options_list:
                item_options[k] = v
        item_options['slug'] = urlify(kwds['name'])
        
        if kwds['identifier'] in self.data['item_by_identifier']:
            item = self.data['item_by_identifier'][kwds['identifier']]
            for k, v in item_options.iteritems():
                setattr(item, k, v)
            item.save()
 
            self.data['item_by_identifier'].update({item.identifier: item})
            logging.debug('[U] %s' % kwds['name'])
            # True if created
            return False
        else:
            item = Item(**item_options)
            item.save()

            tree_item = TreeItem(parent=kwds['parent'], content_object=item)
            tree_item.save()
            
            self.data['item_by_identifier'].update({item.identifier: item})
            logging.debug('[S] %s' % item.name)
            # True if created
            return True

    @transaction.commit_on_success
    def make_items(self, reader):
        try:
            import_section = Section.objects.get(name=u'Импорт')
            self.import_section = import_section.tree.get()
        except Section.DoesNotExist:
            self.import_section = self._get_or_create_section(u'Импорт', None)

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
        options = {}
        options['identifier'] = param_list[0]
        options['quantity'] = param_list[1]
        options['wholesale_price'] = param_list[4]
        options['price'] = param_list[5]
        if len(param_list) == 7:
            options['barcode'] = param_list[6]
        else:
            options['barcode'] = None
        options['name'] = param_list[3].decode('cp1251').replace('""', '"')
        options['slug'] = urlify(options['name'])
        options['short_description'] = options['name'].split(' ').pop()
        section_name = param_list[2].decode('cp1251')
        section_tree_item = self._get_or_create_section(section_name, self.import_section)
        options['parent'] = section_tree_item

        return self._update_or_create_item(**options)

