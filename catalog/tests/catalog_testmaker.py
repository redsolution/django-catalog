# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from django import template
from django.db.models import get_model

class Testmaker(TestCase):

    fixtures = ["../fixtures/catalog_test.json"]

    def test_catalog_130678729224(self):
        r = self.client.get('/catalog/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['paginator']), u'None')
        self.assertEqual(unicode(r.context[-1]['object_list']), u'[<TreeItem: Импорт>]')
        self.assertEqual(unicode(r.context[-1]['is_paginated']), u'False')
        self.assertEqual(unicode(r.context[-1]['page_obj']), u'None')
    def test_catalogsectionimport_130678729379(self):
        r = self.client.get('/catalog/section/import/', {})
        self.assertEqual(r.status_code, 200)
    def test_catalogsectionhuanshan_maofen__130678729524(self):
        r = self.client.get('/catalog/section/huanshan-maofen-/', {})
        self.assertEqual(r.status_code, 200)
    def test_catalogitemhuanshan_maofen_150__130678729647(self):
        r = self.client.get('/catalog/item/huanshan-maofen-150-/', {})
        self.assertEqual(r.status_code, 200)
    def test_catalogitemhuanshan_maofen_480__130678729846(self):
        r = self.client.get('/catalog/item/huanshan-maofen-480-/', {})
        self.assertEqual(r.status_code, 200)
    def test_catalogitemhuanshan_maofen_600__130678729993(self):
        r = self.client.get('/catalog/item/huanshan-maofen-600-/', {})
        self.assertEqual(r.status_code, 200)
    def test_admincatalogtreeitem_130678730548(self):
        r = self.client.get('/admin/catalog/treeitem/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['app_path']), u'/admin/catalog/treeitem/')
        self.assertEqual(unicode(r.context[-1]['title']), u'Log in')
        self.assertEqual(unicode(r.context[-1]['root_path']), u'None')
        self.assertEqual(unicode(r.context[-1]['next']), u'/admin/catalog/treeitem/')
    def test_admincatalogtreeitemdirectproviderjs_130678730598(self):
        r = self.client.get('/admin/catalog/treeitem/direct/provider.js', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['app_path']), u'/admin/catalog/treeitem/direct/provider.js')
        self.assertEqual(unicode(r.context[-1]['title']), u'Log in')
        self.assertEqual(unicode(r.context[-1]['root_path']), u'None')
        self.assertEqual(unicode(r.context[-1]['next']), u'/admin/catalog/treeitem/direct/provider.js')
    def test_admincatalogtreeitemdirectrouter_130678730642(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"colmodel","method":"get_col_model","data":null,"type":"rpc","tid":2},{"action":"colmodel","method":"get_models","data":null,"type":"rpc","tid":3}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678730655(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":["root"],"type":"rpc","tid":4},{"action":"treeitem","method":"objects","data":[{"parent":"root"}],"type":"rpc","tid":5}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678730796(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":6}': '', })
    def test_admincatalogtreeitemdirectrouter_13067873088(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"objects","data":[{"parent":1}],"type":"rpc","tid":7}': '', })
    def test_admincatalogtreeitemdirectrouter_130678731525(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"move_to","data":[{"source":[21,16,14,12,10,8,5,2],"target":"root","point":"append"}],"type":"rpc","tid":8},{"action":"treeitem","method":"tree","data":["root"],"type":"rpc","tid":9}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678731602(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":10},{"action":"treeitem","method":"objects","data":[{"parent":"root"}],"type":"rpc","tid":11}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678731785(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"objects","data":[{"parent":2}],"type":"rpc","tid":12}': '', })
    def test_admindefaultsitem2_130678731926(self):
        r = self.client.get('/admin/defaults/item/2/', {'_popup': '1', })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['app_path']), u'/admin/defaults/item/2/?_popup=1')
        self.assertEqual(unicode(r.context[-1]['title']), u'Log in')
        self.assertEqual(unicode(r.context[-1]['root_path']), u'None')
        self.assertEqual(unicode(r.context[-1]['next']), u'/admin/defaults/item/2/?_popup=1')
    def test_admindefaultsitem2_130678732178(self):
        r = self.client.post('/admin/defaults/item/2/', {'defaults-catalogimage-content_type-object_id-0-id': '', 'description': '', '_save': 'Save', 'defaults-catalogimage-content_type-object_id-__prefix__-id': '', 'price': '250', 'defaults-catalogimage-content_type-object_id-__prefix__-image': '', 'defaults-catalogimage-content_type-object_id-TOTAL_FORMS': '1', '_popup': '1', 'defaults-catalogimage-content_type-object_id-0-image': '', 'defaults-catalogimage-content_type-object_id-INITIAL_FORMS': '0', 'defaults-catalogimage-content_type-object_id-MAX_NUM_FORMS': '', 'article': '2', 'csrfmiddlewaretoken': '2dab25ff69e42a285812adf92949bbb7', 'quantity': '', 'slug': 'shou-mej-cha-chzhuan-chajnyij-kirpich-brovi-dolgoletiya-', 'name': 'Шоу Мэй Ча Чжуань (Чайный кирпич Брови долголетия). ', '_popup': '1', })
    def test_admincatalogtreeitemdirectrouter_130678732217(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":[2],"type":"rpc","tid":13},{"action":"treeitem","method":"objects","data":[{"parent":2}],"type":"rpc","tid":14}]': '', })
    def test_catalogsectionbelyij_chaj_baj_cha__130678732498(self):
        r = self.client.get('/catalog/section/belyij-chaj-baj-cha-/', {})
        self.assertEqual(r.status_code, 200)
    def test_catalogitemshou_mej_to_cha__130678733045(self):
        r = self.client.get('/catalog/item/shou-mej-to-cha-/', {})
        self.assertEqual(r.status_code, 200)
    def test_admindefaultsitem1_130678733339(self):
        r = self.client.get('/admin/defaults/item/1/', {'_popup': '1', })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['app_path']), u'/admin/defaults/item/1/?_popup=1')
        self.assertEqual(unicode(r.context[-1]['site_name']), u'example.com')
        self.assertEqual(unicode(r.context[-1]['title']), u'Log in')
        self.assertEqual(unicode(r.context[-1]['root_path']), u'None')
        self.assertEqual(unicode(r.context[-1]['site']), u'example.com')
        self.assertEqual(unicode(r.context[-1]['next']), u'/admin/defaults/item/1/?_popup=1')
    def test_admindefaultsitem1_130678733575(self):
        r = self.client.post('/admin/defaults/item/1/', {'defaults-catalogimage-content_type-object_id-0-id': '', 'description': '', '_save': 'Save', 'defaults-catalogimage-content_type-object_id-__prefix__-id': '', 'price': '100', 'defaults-catalogimage-content_type-object_id-__prefix__-image': '', 'defaults-catalogimage-content_type-object_id-TOTAL_FORMS': '1', '_popup': '1', 'defaults-catalogimage-content_type-object_id-0-image': '', 'defaults-catalogimage-content_type-object_id-INITIAL_FORMS': '0', 'defaults-catalogimage-content_type-object_id-MAX_NUM_FORMS': '', 'article': '1', 'csrfmiddlewaretoken': '2dab25ff69e42a285812adf92949bbb7', 'quantity': '', 'slug': 'shou-mej-to-cha-', 'name': 'Шоу Мэй То Ча ', '_popup': '1', })
    def test_admincatalogtreeitemdirectrouter_130678733607(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":[2],"type":"rpc","tid":15},{"action":"treeitem","method":"objects","data":[{"parent":2}],"type":"rpc","tid":16}]': '', })
    def test_catalogitemshou_mej_to_cha__13067873376(self):
        r = self.client.get('/catalog/item/shou-mej-to-cha-/', {})
        self.assertEqual(r.status_code, 404)
    def test_admincatalogtreeitemdirectrouter_130678735248(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"objects","data":[{"parent":"root"}],"type":"rpc","tid":17}': '', })
    def test_admindefaultssection2_130678735356(self):
        r = self.client.get('/admin/defaults/section/2/', {'_popup': '1', })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['app_path']), u'/admin/defaults/section/2/?_popup=1')
        self.assertEqual(unicode(r.context[-1]['title']), u'Log in')
        self.assertEqual(unicode(r.context[-1]['root_path']), u'None')
        self.assertEqual(unicode(r.context[-1]['next']), u'/admin/defaults/section/2/?_popup=1')
    def test_admindefaultssection2_130678735557(self):
        r = self.client.post('/admin/defaults/section/2/', {'defaults-catalogimage-content_type-object_id-0-id': '', 'description': '', '_save': 'Save', 'defaults-catalogimage-content_type-object_id-__prefix__-id': '', 'defaults-catalogimage-content_type-object_id-__prefix__-image': '', 'defaults-catalogimage-content_type-object_id-TOTAL_FORMS': '1', '_popup': '1', 'defaults-catalogimage-content_type-object_id-INITIAL_FORMS': '0', 'defaults-catalogimage-content_type-object_id-MAX_NUM_FORMS': '', 'defaults-catalogimage-content_type-object_id-0-image': '', 'csrfmiddlewaretoken': '2dab25ff69e42a285812adf92949bbb7', 'slug': 'belyij-chaj-baj-cha-', 'name': 'Белый Чай (Бай Ча) ', '_popup': '1', })
    def test_admincatalogtreeitemdirectrouter_130678735594(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":["root"],"type":"rpc","tid":18},{"action":"treeitem","method":"objects","data":[{"parent":"root"}],"type":"rpc","tid":19}]': '', })
    def test_catalogsectionbelyij_chaj_baj_cha__130678735753(self):
        r = self.client.get('/catalog/section/belyij-chaj-baj-cha-/', {})
        self.assertEqual(r.status_code, 404)
    def test_admincatalogtreeitemdirectrouter_130678736272(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"remove_objects","data":[{"objects":[2]}],"type":"rpc","tid":20},{"action":"treeitem","method":"tree","data":["root"],"type":"rpc","tid":21}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678736568(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"objects","data":[{"parent":1}],"type":"rpc","tid":22}': '', })
    def test_admincatalogtreeitemdirectrouter_130678736841(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"move_to","data":[{"source":[23],"target":32,"point":"above"}],"type":"rpc","tid":23}': '', })
    def test_admincatalogtreeitemdirectrouter_130678736858(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":24}': '', })
    def test_admincatalogtreeitemdirectrouter_13067873700(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"move_to","data":[{"source":[34],"target":28,"point":"above"}],"type":"rpc","tid":25}': '', })
    def test_admincatalogtreeitemdirectrouter_130678737017(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":26}': '', })
    def test_admincatalogtreeitemdirectrouter_130678737149(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"move_to","data":[{"source":[23],"target":34,"point":"above"}],"type":"rpc","tid":27}': '', })
    def test_admincatalogtreeitemdirectrouter_130678737166(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":28}': '', })
    def test_admincatalogtreeitemdirectrouter_130678737258(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"move_to","data":[{"source":[23],"target":32,"point":"above"}],"type":"rpc","tid":29}': '', })
    def test_admincatalogtreeitemdirectrouter_130678737275(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":30}': '', })
    def test_admincatalogtreeitemdirectrouter_130678737865(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"move_to","data":[{"source":[34],"target":5,"point":"below"}],"type":"rpc","tid":31},{"action":"treeitem","method":"tree","data":["root"],"type":"rpc","tid":32}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678737884(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":33},{"action":"treeitem","method":"objects","data":[{"parent":"root"}],"type":"rpc","tid":34}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678738845(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"move_to","data":[{"source":[5],"target":5,"point":"below"}],"type":"rpc","tid":35},{"action":"treeitem","method":"tree","data":["root"],"type":"rpc","tid":36}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678738859(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"tree","data":[1],"type":"rpc","tid":37},{"action":"treeitem","method":"objects","data":[{"parent":"root"}],"type":"rpc","tid":38}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678739342(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"move_to","data":[{"source":[5],"target":8,"point":"above"}],"type":"rpc","tid":39},{"action":"treeitem","method":"objects","data":[{"parent":8}],"type":"rpc","tid":40}]': '', })
    def test_admincatalogtreeitemdirectrouter_130678739779(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'[{"action":"treeitem","method":"move_to","data":[{"source":[10],"target":8,"point":"append"}],"type":"rpc","tid":41},{"action":"treeitem","method":"tree","data":[8],"type":"rpc","tid":42},{"action":"treeitem","method":"objects","data":[{"parent":8}],"type":"rpc","tid":43}]': '', })
    def test_admincatalogtreeitemdirectrouter_13067873995(self):
        r = self.client.post('/admin/catalog/treeitem/direct/router/', {'{"action":"treeitem","method":"objects","data":[{"parent":8}],"type":"rpc","tid":44}': '', })
