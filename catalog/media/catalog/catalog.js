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
    	var dragElements = [];
        if (source.grid) {
            for (var i = 0; i < source.dragData.selections.length; i++) {
            	r = source.dragData.selections[i]
                dragElements.push(r.id);
                //r.store.remove(r);
            }
            var index = source.getDragData(e).rowIndex;
            targetElement = source.grid.store.getAt(index);
        } else {
            // Drop from tree not supported yet...
            return false;
        }
        Catalog.treeitem.move_to({source: dragElements, target: targetElement.id, point: 'above'})
        

        return false;
    },
    on_tree_drop: function(dd, e, data) {
    	// disables the animated repair
    	dd.tree.dragZone.proxy.animRepair = false;
    	
    	// cancels the drag&drop operation
    	dd.cancel = true;
    	
    	// display the modal confirm dialog
    	Ext.Msg.confirm('Confirmation', 'Are  you sure you want to move this item?', function(button){
    		// the animated repair is enabled again
    		dd.tree.dragZone.proxy.animRepair = true;
    		
	        if (button == 'yes') {
	        	switch (dd.point) {
	                case "append":
	                	if (dd.source.tree)
	                		dd.target.appendChild(dd.dropNode);
	                    break;
	                case "above":
	                	if (dd.source.tree)
	                    	dd.target.parentNode.insertBefore(dd.dropNode, dd.target);
	                    break;
	                case "below":
	                	if (dd.source.tree)
	                    	dd.target.parentNode.insertBefore(dd.dropNode, dd.target.nextSibling);
	                    break;
	                default:
	                    debugger;
	            }
	        }
    	});
    	
    	var dragElements = [];
        if (dd.source.tree) {
        	dragElements.push(dd.data.node.id);
        } else if (dd.source.grid) {
    	    for(var i = 0; i < dd.data.selections.length; i++) {
    	    	var r = dd.data.selections[i];
    	    	dragElements.push(r.id);
    	    	r.store.remove(r);
    	    }
    	}

		Catalog.treeitem.move_to({source: dragElements, target: dd.target.id, point: dd.point});

		if (dd.source.grid) {
			var target_node = null;
	    	if ( dd.point == 'below' || dd.point == 'above' ) {
	    		target_node = dd.target.parentNode;
	    	} else {
	    		target_node = dd.target;
	    	}
	    	console.log(dd.point, dd.target.getPath());
	    	
	    	app.tree.getRootNode().reload();
	    	app.tree.expandPath(target_node.getPath());
	    }
		return true;
   	},
   	on_node_select: function(node, event) {
   		if (node.leaf == false) {
   			app.store.load({params: {'parent': node.id}});
   		} else {
   			app.store.load({params: {'id': node.id}});
   		}
   }
    
}


/** ** Catalog app layout building *** */
app.build_layout = function(){
    app.store = new Ext.data.DirectStore({
        storeId: 'DataStore',
        directFn: Catalog.treeitem.objects,
        autoLoad: false,
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
        tbar: new Ext.Toolbar({
        	items: [
        	{
	        	text: 'Add',
	        	handler: function(btn, ev) {
	            	console.log('add');
	            },
	        	cls: 'x-btn-text',
        	}, '-', {
	        	text: 'Delete',
	        	handler: function(btn, ev) {
	        		console.log('del');
	        	},
	        	cls: 'x-btn-text',
        	}, '-', {
	        	text: 'Reload',
	        	handler: function(btn, ev) {
	            	app.store.load();
	            },
	        	cls: 'x-btn-text',
        	}, '-',]
        }),
        bbar: new Ext.PagingToolbar({
            pageSize: 10,
            displayInfo: true,
            store: app.store
        }),
        listeners: {
            'render': function() {
                // Enable sorting Rows via Drag & Drop
                new Ext.dd.DropTarget(this.container, {
                    ddGroup: 'dd',
                    copy: false,
                    notifyDrop: app.callbacks.on_grid_drop
                });
            }
        },

    });
    
    app.tree = new Ext.tree.TreePanel({
        title: 'Tree',
        useArrows: true,
        autoScroll: true,
        containerScroll: true,
        root: {
            id: 'root',
            text: 'Catalog'
        },
        ddGroup: 'dd',
        enableDD: true,
        loader: new Ext.tree.TreeLoader({
        	preloadChildren:true,
            directFn: Catalog.treeitem.tree
        }),
        listeners: {
            beforenodedrop: app.callbacks.on_tree_drop,
            click: app.callbacks.on_node_select,
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
            width: 300,
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
