;
/** ** Django CSRF workaround *** */
Ext.Ajax.on('beforerequest', function (conn, options) {
       if (!(/^http:.*/.test(options.url) || /^https:.*/.test(options.url))) {
         if (typeof(options.headers) == "undefined") {
           options.headers = {'X-CSRFToken': Ext.util.Cookies.get('csrftoken')};
         } else {
           options.headers.extend({'X-CSRFToken': Ext.util.Cookies.get('csrftoken')});
         }                        
       }
    }, this);

var app={};

/** ExtDirect Exception handling */
Ext.Direct.on('exception', function(e){
    if (e.type === Ext.Direct.exceptions.SERVER) {
        var msg = 'An error occured in action: ' + e.action +
            ' method: ' + e.method + '<br />' +
            '<b>Traceback</b>:<br />' +
            '<tt>' + e.where + '</tt>';
        Ext.Msg.alert(e.message, msg);
    }
});

/** ** bind server data events to asynchronous handlers *** */ 
app.direct_data_listener = function(provider, event){
    if (event.action === 'colmodel' && event.method === 'get_col_model') {
        app.direct_handlers.on_get_col_model(provider, event);
    }
};
app.direct_handlers = {
    on_get_col_model: function(provider, event) {
        app.colmodel = event.result;
        app.build_layout();
    }
};

app.callbacks = {
    on_grid_drop: function(source, e, data) {
        if (source.grid) {
            var i;
            var dragElements = [];
            for (i=0;i<source.dragData.selections.length;i++) {
                dragElements.push(source.dragData.selections[i].id);
            }
            var index=source.getDragData(e).rowIndex;
            targetElement = source.grid.store.getAt(index);
        } else {
            // Drop from tree not supported yet...
            return false;
        }
        console.log('insert ' + dragElements + ' at ' + targetElement.id);
        return false;
    },
    on_tree_drop: function(dd, e, data) {
        console.log('Tree drop event!');
        console.log(dd, e, data);
    }
}


/** ** Catalog app layout building *** */
app.build_layout = function(){
    app.store = new Ext.data.DirectStore({
        storeId: 'DataStore',
        directFn: Catalog.treeitem.objects,
        autoLoad: true,
        remoteSort: true,
        root: 'records',
        fields: app.colmodel
    });
    
    app.grid = new Ext.grid.GridPanel({
        store: app.store,
        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
        cm:  new Ext.grid.ColumnModel({
            columns: app.colmodel
        }),
        ddGroup: 'dd',
        maskDisabled : true,
        enableDragDrop: true,
        bbar: new Ext.PagingToolbar({
            pageSize: 50,
            displayInfo: true,
            store: app.store
        }),
        listeners: {
            'render': function() {
                // Enable sorting Rows via Drag & Drop
                new Ext.dd.DropTarget(this.container, {
                    ddGroup : 'dd',
                    copy:false,
                    notifyDrop : app.callbacks.on_grid_drop
                });
            }
        }
    });
    
    app.tree = new Ext.tree.TreePanel({
        title: 'Tree',
        root: {
            id: 'root',
            text: 'Catalog'
        },
        ddGroup: 'dd',
        enableDD: true,
        loader: new Ext.tree.TreeLoader({
            directFn: Catalog.treeitem.tree
        }),
        listeners: {
            'beforenodedrop': app.callbacks.on_tree_drop
        }
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
};

/** ** Application initialization part *** */

Ext.onReady(function() {
    Ext.QuickTips.init();

    var provider = Ext.Direct.getProvider('catalog_provider');
    provider.on('data', app.direct_data_listener);

    Catalog.colmodel.get_col_model();

});
