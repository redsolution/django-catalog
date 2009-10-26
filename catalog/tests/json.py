from catalog.models import *
from catalog.admin.utils import get_connected_models
from django.test import TestCase
from django.test.client import Client


class Testjson(TestCase):
    '''Testing json output for admin interface
    Catalog structure:
        section1
            item1
            item2
        section2
            metaitem1
                item3
                item4
    '''
    fixtures = ['auth']
    
    def setUp(self):
        '''tes up test'''
        def do_item(name, Model, parent):
            instance = Model(name=name)
            instance.save()
            setattr(self, '%s' % name, instance)
            
            treeitem = TreeItem(content_object=instance, parent=parent)
            treeitem.save()
            setattr(self, '%s_tree' % name, treeitem)
        
        do_item('section1', Section, None)
        do_item('section2', Section, None)
        
        do_item('metaitem1', MetaItem, self.section2_tree)
        
        do_item('item1', Item, self.section1_tree)
        do_item('item2', Item, self.section1_tree)
        do_item('item3', Item, self.metaitem1_tree)
        do_item('item4', Item, self.metaitem1_tree)
        
    def testTree(self):
        '''Test ext_tree works'''  
        for model, admin in get_connected_models():
            model.objects.all()[0].ext_tree()
    
    def testGrid(self):
        '''Test ext_grid wokrs'''
        for model, admin in get_connected_models():
            model.objects.all()[0].ext_tree()
    
    def testMove(self):
        '''Moving nodes. Only default models supported'''
        client = Client()
        if not client.login(username='root', password='password'):
            raise("auth.json is not installed, can't login")

        def do_test(action, source, target, allow, assert_message):
            '''helper for increase readability'''
            response = client.post('/admin/catalog/json/move', {
                'point': action,
                'source': source.id,
                'target': target.id,
            })
            if allow:
                self.assertEqual(response.status_code, 200, assert_message)
            else:
                self.assertEqual((response.status_code, response.content),
                    (500, 'Can not move'), 'Move item in item failed')

        # move item1 in section2
        do_test('append', self.item1_tree, self.section2_tree, True, 'Move item in section failed')

        # move item2 in metaitem1
        do_test('append', self.item2_tree, self.metaitem1_tree, True, 'Move item in metaitem failed')

        # move item3 in item4
        do_test('append', self.item3_tree, self.item4_tree, False, 'Move item in item failed')

        # move section1 in section2
        do_test('append', self.section1_tree, self.section2_tree, True, 'Move section in section failed')

        # move item1 above to section1
        do_test('above', self.item1_tree, self.section2_tree, True, 'Move item above section failed')

        # move item1 below to section1
        do_test('below', self.item1_tree, self.section2_tree, True, 'Move item below section failed')

    def testVisible(self):
        '''Test visible button'''
        client = Client()
        if not client.login(username='root', password='password'):
            raise("auth.json is not installed, can't login")

        # hide
        response = client.post('/admin/catalog/json/visible', {
            'items': '%s' % (self.item1_tree.id),
            'visible': 0,
        })
        self.assertEqual(response.status_code, 200)
        self.failIf(self.item1_tree.content_object in Item.objects.filter(show=True),
            'Visible hide failed')

        # show
        response = client.post('/admin/catalog/json/visible', {
            'items': '%s' % (self.item1_tree.id),
            'visible': 1,
        })
        self.assertEqual(response.status_code, 200)
        self.failIf(self.item1_tree.content_object in Item.objects.filter(show=False),
            'Visible show failed')

    def testRelTree(self):
        '''Test tree many-to-many relation editor'''
