# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
import csv
from time import time
from datetime import datetime
from upload.models import ImportItem
from django.template.loader import render_to_string
from django.conf import settings
from os import path
from pyExcelerator import Workbook, XFStyle, Alignment, Font
import logging


class Command(BaseCommand):
    help = '''Import items to template price'''

    option_list = BaseCommand.option_list + (
        make_option('--verbose', default=None, dest='verbose', type='int',
            help='Verbose level 0, 1 or 2 (0 by default)'),
        make_option('--whole', default=False, dest='whole', type='string',
            help='wholeprice'),
    )
    
    def handle(self, *args, **options):
        start_time = time()
        self.options = options
        
        if self.options['verbose'] == 2:
            logging.getLogger().setLevel(logging.DEBUG)
        elif self.options['verbose'] == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif self.options['verbose'] == 0:
            logging.getLogger().setLevel(logging.ERROR)
        
        last_item = ImportItem.objects.filter(ok=True).latest('date_loaded')
        if not last_item:
            raise CommandError('No import files')
        src = last_item.file.path
        
        class csv_format(csv.Dialect):
            delimiter = ';'
            quotechar = '"'
            doublequote = True
            lineterminator = '\r\n'
            quoting = csv.QUOTE_MINIMAL

        reader = csv.reader(open(src, 'r'), dialect=csv_format)
        count = 0
        
        if self.options['verbose'] >= 1:
            logging.info('Importing items')
        
        for item in reader:
            try:
                self.make_item(item)
            except ValueError:
                if self.options['verbose'] >= 2:
                    logging.error('Error importing record: %s' % item)
            count = count + 1
        self.write_html_price()
        self.write_xls_price()

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
        if self.options['whole']:
            options['price'] = param_list[4]
        else:
            options['price'] = param_list[5]
        if len(param_list) == 7:
            options['barcode'] = param_list[6]
        else:
            options['barcode'] = None
        options['name'] = param_list[3].decode('cp1251').replace('""', '"')
        options['short_description'] = options['name'].split(' ').pop()
        section_name = param_list[2].decode('cp1251')
        section = self._get_or_create_section(section_name)
        options['parent'] = section

        return self._create_item(**options)
    
    def write_html_price(self):
        content = render_to_string('catalog/price.html', {'sections': self.data})
        if self.options['whole']:
            filename = path.join(settings.MEDIA_ROOT, 'upload/wprice.html')
        else:
            filename = path.join(settings.MEDIA_ROOT, 'upload/price.html')

        f = open(filename, 'w')
        f.write(content.encode('utf-8'))
        f.close()

    def write_xls_price(self):
        if self.options['whole']:
            filename = path.join(settings.MEDIA_ROOT, 'upload/wprice.xls')
        else:
            filename = path.join(settings.MEDIA_ROOT, 'upload/price.xls')
        workBookDocument = Workbook()
        docSheet = workBookDocument.add_sheet(u'Прайс соло-парфюм')
        docSheet.col(1).width = 10000
        headerFont = Font()
        headerFont.bold = True
        headerFont.size = 400
        headerStyle = XFStyle()
        headerStyle.font = headerFont
        docSheet.row(0).set_style(headerStyle)
        if self.options['whole']:
            docSheet.write_merge(0, 0, 0, 2, u'Оптовый прайс-лист Соло-парфюм (%s)' % datetime.now().strftime('%d.%m.%Y'))
        else:
            docSheet.write_merge(0, 0, 0, 2, u'Прайс-лист Соло-парфюм (%s)' % datetime.now().strftime('%d.%m.%Y'))

        docSheet.write(2, 0, u'Артикул')
        docSheet.write(2, 1, u'Наименование', )
        docSheet.write(2, 2, u'Цена')

        sectionFont = Font()
        sectionFont.bold = True
        sectionStyle = XFStyle()
        sectionStyle.font = sectionFont
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        sectionStyle.alignment = align

        row = 3
        for section in self.data.iterkeys():
            docSheet.write_merge(row, row, 0, 2, section, sectionStyle)
            row += 1
            for item in self.data[section]:
                docSheet.write(row, 0, item['identifier'])
                docSheet.write(row, 1, item['name'])
                docSheet.write(row, 2, item['price'])
                row += 1

        workBookDocument.save(filename)

