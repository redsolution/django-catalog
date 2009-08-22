# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
from catalog.models import TreeItem, Section, Item
import csv
from urlify import urlify
from time import time
from django.db import transaction, connection


class Command(BaseCommand):
    help = '''Import items from CommerceML format
    Usage: manage.py importcml filename.xml
    '''
    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=None, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
    )
    
    
    def handle(self, *args, **options):
        start_time = time()
        self.options = options

        if len(args) == 0:
            raise CommandError("You should specify file to import")
        filename = args[0]

        class csv_format(csv.Dialect):
            delimiter = ';'
            quotechar = '"'
            doublequote = True
            lineterminator = '\r\n'
            quoting = csv.QUOTE_MINIMAL
            
#===============================================================================
#        Preparing
#===============================================================================

        reader = csv.reader(open(filename, 'r'), dialect=csv_format)
        count = 0

        if self.options['verbose'] >= 2:
            print 'Loading objects'
        self.load_objects()
        
#===============================================================================
#        Run!
#===============================================================================

        try:
            self.import_section = Section.get(tree__name=u'Импорт')
        except:
            self.import_section = self._get_or_create_section(u'Импорт', None)
        
        if self.options['verbose'] >= 1:
            print 'Importing items'        
        
        for item in reader:
#            try:
            start_make = time()
            self.make_item(item)
            make_time = time() - start_make
            if make_time > 0.5:
                if self.options['verbose'] >= 2:
                    print '[*] reindexing table...'
                self.reindex_db()
                
#            except ValueError:
#                if self.options['verbose'] >= 2:
#                    print 'Error importing record:', item
            count = count + 1

        work_time = time() - start_time
        if self.options['verbose'] >= 1:
            print count, 'items imported in %s s' % work_time
            
    def load_objects(self):
        
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

        
        #  load treeitems
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
            
            if self.options['verbose'] >= 2:
                print '[S]', '=== %s ===' % section
            return section_tree_item

    def _update_or_create_item(self, **kwds):
        item_options = {}
        item_options['price'] =  kwds['price']
        item_options['quantity'] =  kwds['quantity']
        item_options['barcode'] =  kwds['barcode']
        item_options['identifier'] =  kwds['identifier']
        item_options['short_description'] =  kwds['short_description']
        item_options['name'] =  kwds['name']
        item_options['slug'] = urlify(kwds['name'])
        
        if kwds['identifier'] in self.data['item_by_identifier']:
            item = self.data['item_by_identifier'][kwds['identifier']]
            item.price = item_options['price']
            item.quantity = item_options['quantity']
            item.barcode = item_options['barcode']
            item.name = item_options['name']
            item.slug = item_options['slug']
            item.save()
            if self.options['verbose'] >= 2:
                print '[U]', kwds['name']
            # True if created
            return False
        else:
            item = Item(**item_options)
            item.save()

            tree_item = TreeItem(parent=kwds['parent'], content_object=item)
            tree_item.save()

            if self.options['verbose'] >= 2:
                print '[S]', item.name
            # True if created
            return True

    @transaction.commit_on_success
    def make_item(self, param_list):
        '''
        Makes a new item in catalog
        param_list = [identifier, quantity, '<section_name> <name>']
        '''
        options = {}
        options['identifier'] = param_list[0]
        options['quantity'] = param_list[1]
        options['price'] = param_list[4]
        if len(param_list) == 6:
            options['barcode'] = param_list[5]
        else:
            options['barcode'] = None
        options['name'] = param_list[3].decode('cp1251').replace('""', '"')
        options['short_description'] = options['name'].split(' ').pop()
        section_name = param_list[2].decode('cp1251')
        section_tree_item = self._get_or_create_section(section_name, self.import_section)
        options['parent'] = section_tree_item

        return self._update_or_create_item(**options)
    
    def reindex_db(self):
        cursor = connection.cursor()
        cursor.execute('''
        REINDEX TABLE catalog_treeitem FORCE;
        ''')