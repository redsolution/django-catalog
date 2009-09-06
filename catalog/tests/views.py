from catalog.models import *
from catalog.admin.utils import get_connected_models
from django.test import TestCase
from django.test.client import Client


class Testviews(TestCase):
    '''Testing views for admin interface
    Catalog structure:
        section1
        item1
        metaitem1
    '''
    fixtures = ['auth']

    def setUp(self):
        '''tes up test'''
        def do_test(name, Model, parent):
            instance = Model(name=name)
            instance.save()
            setattr(self, '%s' % name, instance)

            treeitem = TreeItem(content_object=instance, parent=parent)
            treeitem.save()
            setattr(self, '%s_tree' % name, treeitem)

        do_test('section1', Section, None)
        do_test('metaitem1', MetaItem, None)
        do_test('item1', Item, None)

    def testIndex(self):
        '''Test index admin page'''
        client = Client()
        self.assert_(client.login(username='root', password='password'),
            "auth.json is not installed, can't login")
        response = client.get('/admin/catalog/')
        self.assertEqual(response.status_code, 200, "Admin index page doesn't exixst")

    def testAdd(self):
        '''Test new element addition'''
        client = Client()
        self.assert_(client.login(username='root', password='password'),
            "auth.json is not installed, can't login")

        def do_test(model_cls):
            model_name = model_cls.__name__.lower()
            response = client.get('/admin/catalog/new%s' % model_name, {'parent': 'root'})
            self.assertEqual(response.status_code, 302)
            self.failUnless(model_cls.objects.all().count() == 2, 'New %s failed' % model_name)

        # add new item
        do_test(Item)
        # add new metaitem
        do_test(MetaItem)
        # add new section
        # TODO: fix fail here
        do_test(Section)

    def testEdit(self):
        '''Test edit forms displayed'''
        client = Client()
        self.assert_(client.login(username='root', password='password'),
            "auth.json is not installed, can't login")

        # edit item
        response = client.get('/admin/catalog/item/%s/' % self.item1.id)
        self.assertEqual(response.status_code, 200, 'Item edit form not displaying')

        # edit metaitem
        response = client.get('/admin/catalog/metaitem/%s/' % self.metaitem1.id)
        self.assertEqual(response.status_code, 200, 'MetaItem edit form not displaying')

        # edit section
        response = client.get('/admin/catalog/section/%s/' % self.section1.id)
        self.assertEqual(response.status_code, 200, 'Section edit form not displaying')

    def testRedirects(self):
        '''Test editor redirects works'''
        client = Client()
        self.assert_(client.login(username='root', password='password'),
            "auth.json is not installed, can't login")

        def do_test(instance, model_name):
            response = client.get('/admin/catalog/edititem/%s/' % instance.id)
            self.assertEqual(response.status_code, 302, 'Can not redirect to %s' % model_name)

        # test item redirect
        do_test(self.item1_tree, 'Item')
        # test metaitem redirect
        do_test(self.metaitem1_tree, 'MetaItem')
        # test section redirect
        do_test(self.section1_tree, 'Section')
