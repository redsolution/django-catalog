;var app={};

Ext.Ajax.on('beforerequest', function (conn, options) {
	   if (!(/^http:.*/.test(options.url) || /^https:.*/.test(options.url))) {
	     if (typeof(options.headers) == "undefined") {
	       options.headers = {'X-CSRFToken': Ext.util.Cookies.get('csrftoken')};
	     } else {
	       options.headers.extend({'X-CSRFToken': Ext.util.Cookies.get('csrftoken')});
	     }                        
	   }
	}, this);

Ext.onReady(function() {
    Ext.QuickTips.init();
    
    app.store = new Ext.data.DirectStore({
        storeId: 'DataStore',
        directFn: Catalog.treeitem.objects,
        autoLoad: true,
        remoteSort: true,
        root: 'records',
        fields: ['id', 'content_type','object_id','parent','tree_id']
    });
    
    app.grid = new Ext.grid.GridPanel({
        store: app.store,
        title: 'Grid!',
        sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
        cm:  new Ext.grid.ColumnModel({
            columns: [{
                header: 'ID',
                dataIndex: 'id'
            },{
                header: 'Content type',
                dataIndex: 'content_type'
            },{
                header: 'object id',
                dataIndex: 'object_id'
            }]
        })
    });
    
    app.tree = new Ext.tree.TreePanel({
        title: 'Tree!',
        root: {
            id: 'root',
            text: 'Catalog'
        },
        loader: new Ext.tree.TreeLoader({
            directFn: Catalog.treeitem.tree
        }),
        
    });
    
    app.view = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            xtype: 'panel',
            height: 50
        },{
            region: 'center',
            layout: 'fit',
            margins: '15 5 5 5',
            items: app.grid
        },{
            region: 'west',
            width: 200,
            margins: '15 5 5 5',
            layout: 'fit',
            items: app.tree
        }]
    });
    Ext.DomHelper.overwrite('content', '', false);
});
