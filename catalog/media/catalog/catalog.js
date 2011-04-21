;
/**** Django CSRF workaround ****/
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

/**** bind server data events to asynchronous handlers ****/ 
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
	on_grid_drop: function(dd, e, data) {
        var ds = app.store;
        
        console.log('Drop event!');
        console.log(dd, e, data);

        // NOTE:
        // you may need to make an ajax call
        // here
        // to send the new order
        // and then reload the store


        // alternatively, you can handle the
		// changes
        // in the order of the row as
			// demonstrated below

          // ***************************************

//          var sm = grid.getSelectionModel();
//          var rows = sm.getSelections();
//          if(dd.getDragData(e)) {
//              var cindex=dd.getDragData(e).rowIndex;
//              if(typeof(cindex) != "undefined") {
//                  for(i = 0; i <  rows.length; i++) {
//                  ds.remove(ds.getById(rows[i].id));
//                  }
//                  ds.insert(cindex,data.selections);
//                  sm.clearSelections();
//               }
//           }

          // ************************************
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
        enableDragDrop: true,
        listeners: {
        	"render": function() {
		      // Enable sorting Rows via Drag & Drop
		      // this drop target listens for a row drop
		      // and handles rearranging the rows
	              var ddrow = new Ext.dd.DropTarget(this.container, {
	                  ddGroup : 'dd',
	                  copy:false,
	                  notifyDrop : app.callbacks.on_grid_drop
	              	});

              // load the grid store
              // after the grid has been rendered
             this.store.load();
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

/**** Application initialization part ****/

Ext.onReady(function() {
    Ext.QuickTips.init();

    var provider = Ext.Direct.getProvider('catalog_provider');
    provider.on('data', app.direct_data_listener);

    Catalog.colmodel.get_col_model();

});
