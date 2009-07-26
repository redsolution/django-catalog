# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
from catalog.models import TreeItem, Section, Item
import csv
from urlify import urlify
from time import time
from django.db import transaction

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

        reader = csv.reader(open(filename, 'r'), dialect=csv_format)
        count = 0
        if self.options['verbose'] >= 1:
            print 'Importing items'

        try:
            self.import_section = Section.get(tree__name=u'Импорт')
        except:
            self.import_section = self._get_or_create_section(u'Импорт', None)
        for item in reader:
            try:
                self.make_item(item)
            except ValueError:
                if self.options['verbose'] >= 2:
                    print 'Error importing record:', item
            count = count + 1

        work_time = time() - start_time
        if self.options['verbose'] >= 1:
            print count, 'items imported in %s s' % work_time

    def _get_or_create_section(self, name, parent):
        section_tree_item, created = TreeItem.objects.get_or_create(name=name,
            parent=parent)
        if created:
            section_tree_item.slug = urlify(name)
            section = Section()
            section.save()
            section_tree_item.section = section
            section_tree_item.save()
            if self.options['verbose'] >= 2:
                print '[S]', '=== %s ===' % section
        else:
            section = Section.objects.get(tree=section_tree_item)
        return section

    def _update_or_create_item(self, **kwds):
        item, created = Item.objects.get_or_create(identifier=kwds['identifier'])
        if created:
            tree_item = TreeItem(name=kwds['name'], parent=kwds['parent'])
            tree_item.slug = urlify(tree_item.name)
                        
            item.price =  kwds['price']
            item.quantity =  kwds['quantity']
            item.barcode =  kwds['barcode']
            item.save()
            
            tree_item.item = item
            
            tree_item.save()

            if self.options['verbose'] >= 2:
                print '[S]', item.tree.name
        else:
            item.price =  kwds['price']
            item.quantity =  kwds['quantity']
            item.barcode =  kwds['barcode']
            item.tree.name = kwds['name']
            
            item.save()
            item.tree.save()

            if self.options['verbose'] >= 2:
                print '[U]', kwds['name']
        return created
    
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
        section_name = param_list[2].decode('cp1251')
        section = self._get_or_create_section(section_name, self.import_section.tree)
        options['parent'] = section.tree

        return self._update_or_create_item(**options)
