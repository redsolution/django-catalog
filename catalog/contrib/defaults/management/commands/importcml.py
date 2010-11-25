# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sys import argv
from optparse import make_option
from catalog.models import TreeItem, Section, Item

try:
    from xml.etree.ElementTree import fromstring
# python 2.4 fix
except ImportError:
    from elementtree.ElementTree import fromstring

class Offer(dict):
    def __init__(self, xml_tree, *args, **kwds):
        super(Offer, self).__init__(*args, **kwds)
        self.xml_tree = xml_tree
        self['price'] = xml_tree.attrib['Цена'.decode('utf8')]
        self['quantity'] = xml_tree.attrib['Количество'.decode('utf8')]
        self['name'] = self._get_full_name()
        self['identifier'] = self._get_catalog_id()

    def _get_properties(self):
        result_data = {}
        property_values = self.xml_tree.findall('ЗначениеСвойства'.decode('utf8'))
        for property_value in property_values:
            key = property_value.attrib['ИдентификаторСвойства'.decode('utf8')]
            value = property_value.attrib['Значение'.decode('utf8')]
            result_data[key] = value
        return result_data

    def _get_full_name(self):
        properties = self._get_properties()
        return properties['ПолноеНаименование'.decode('utf8')]

    def _get_catalog_id(self):
        item_link = self.xml_tree.find('СсылкаНаТовар'.decode('utf8'))
        return item_link.attrib['ИдентификаторВКаталоге'.decode('utf8')]


class Command(BaseCommand):
    help = '''Export items from CommerceML format
    Usage: manage.py importcml filename.xml 
    '''

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("You should specify file to import")
        filename = args[0]
        xml_file = open(filename, 'r')
        cml = xml_file.read()

        tree = fromstring(cml)
        offers = tree.getchildren()[1].findall('Предложение'.decode('utf-8'))
        for offer in offers:
            self.create_item(Offer(offer))

    def create_item(self, item_params):
        try:
            target_tree_item = TreeItem.objects.get(name=u'Импорт')
        except TreeItem.DoesNotExist:
            target_tree_item = TreeItem(parent_id=None, name=u'Импорт')
            target_tree_item.save()
            target_section = Section(is_meta_item=False)
            target_section.save()
            target_tree_item.section = target_section
            target_tree_item.save()
            
        new_tree_item = TreeItem(name = item_params['name'][:200],
            parent=target_tree_item)
        new_item = Item(
            price = item_params['price'],
            identifier = item_params['identifier'],
            quantity = item_params['quantity'],
        )
        new_tree_item.save()
        new_item.save()
        new_tree_item.item = new_item
        new_tree_item.save()
