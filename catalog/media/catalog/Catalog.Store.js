;Ext.ns('Catalog');
Catalog.GridStore = Ext.extend(Ext.data.DirectStore, {
    constructor: function(cfg) {
        cfg = cfg || {
            storeId: 'DataStore',
            directFn: Catalog.treeitem.objects,
            autoLoad: true,
            remoteSort: true,
            root: 'records',
            fields: ['id', 'content_type','object_id','parent','tree_id']
        };
        Catalog.GridStore.superclass.constructor.call(this, Ext.apply({}, cfg));
    }
});
