# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
import csv
from time import time
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = '''Import items to template price'''

    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=None, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
    )
    
    def handle(self, *args, **options):
        start_time = time()
        self.options = options

        if len(args) == 0:
            raise CommandError("You should specify file to import")
        src = args[0]
        try:
            dst = args[1]
        except IndexError:
            dst = None

        class csv_format(csv.Dialect):
            delimiter = ';'
            quotechar = '"'
            doublequote = True
            lineterminator = '\r\n'
            quoting = csv.QUOTE_MINIMAL

        reader = csv.reader(open(src, 'r'), dialect=csv_format)
        count = 0
        
        if self.options['verbose'] >= 1:
            print 'Importing items'        
        
        for item in reader:
            try:
                self.make_item(item)
            except ValueError:
                if self.options['verbose'] >= 2:
                    print 'Error importing record:', item
            count = count + 1
        self.write_price(dst)

        work_time = time() - start_time
        if self.options['verbose'] >= 1:
            print count, 'items imported in %s s' % work_time
    
    def __init__(self):
        self.data = {}

    def _get_or_create_section(self, name):
        if name not in self.data:
            self.data.update({name: []})
        return name

    def _create_item(self, **kwds):
        
        if int(kwds['quantity']) > 0:
            self.data[kwds['parent']].append(kwds)


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
        section = self._get_or_create_section(section_name)
        options['parent'] = section

        return self._create_item(**options)
    
    def write_price(self, filename):
        content = render_to_string('catalog/price.html', {'sections': self.data})
        if filename is not None:
            f = open(filename, 'w')
            f.write(content.encode('utf-8'))
            f.close()
        else:
            print content