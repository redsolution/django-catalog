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
    
    if (event.action === 'colmodel' && event.method === 'get_models') {
    	var items = [];
    	for (var i = 0; i < event.result.length; i++) {
    		items.push({
    			text: event.result[i].model_name,
    			hrefTarget: event.result[i].url,
    			handler: function (k) {
    				var params={};
    				if (app.tree.selModel.selNode) {
    					if ( app.tree.selModel.selNode.leaf ) {
    						params.parent = app.tree.selModel.selNode.parentNode.id;
    					} else {
    					    params.parent = app.tree.selModel.selNode.id;
    					}
    				} else {
    				    params.parent = app.tree.root.id;
    				}
    				params._popup = 1;
	    			var win = window.open(
	    				k.hrefTarget + '?' + Ext.urlEncode(params),
	    				"",
	    				"menubar=no,width=800,height=730,toolbar=no,scrollbars=yes"
	    			);
	    			win.focus();
    			}
    		});
    	}
    	app.addMenu.add(items);
    }
};

app.direct_handlers = {
    on_get_col_model: function(provider, event) {
        app.colmodel = event.result;
        app.colmodel.push({
	    	xtype: 'actioncolumn',
	    	width: 50,
	    	items: [{
	    		icon: '/static/catalog/img/cog_edit.png',
	    		tooltip: gettext('Change'),
	    		handler: function(grid, rowIndex, colIndex) {
					console.dir(app.store.getAt(rowIndex));
	    			var win = window.open(
	    				app.store.getAt(rowIndex).json.url,
	    				"",
	    				"menubar=no,width=800,height=730,toolbar=no,scrollbars=yes"
	    			);
	    			win.focus();
	            }
	    	},{
	    		icon: '/static/catalog/img/delete.gif',
	    		tooltip: gettext('Delete'),
	    		handler: function(grid, rowIndex, colIndex) {
	    			Ext.Msg.confirm(gettext('Confirmation'), gettext('Are you sure you want to remove this item?'), function(button){
	    				if (button == 'yes') {
							Catalog.treeitem.remove_objects({objects: [app.store.getAt(rowIndex).json.id]});
							app.store.remove(app.store.getById(app.store.getAt(rowIndex).json.id));
	    				}
	    			});
	            }
	    	}]
	    });
        app.build_layout();
    }
};

app.callbacks = {
    on_grid_drop: function(source, e, data) {
    	console.log(e, data);
    	var dragElements = [];
        if (source.grid) {
	        var sm = source.grid.getSelectionModel();
	        var rows = sm.getSelections();
	        var cindex = source.getDragData(e).rowIndex;
	        targetElement = source.grid.store.getAt(cindex);
            for (var i = 0; i < source.dragData.selections.length; i++) {
            	r = source.dragData.selections[i]
                dragElements.push(r.id);
                
                app.store.remove(app.store.getById(rows[i].id));
                app.store.insert(cindex,rows[i]);
            }
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
    	Ext.Msg.confirm(gettext('Confirmation'), gettext('Are you sure you want to move this item?'), function(button){
    		// the animated repair is enabled again
    		dd.tree.dragZone.proxy.animRepair = true;
    		
	        if (button == 'yes') {
		    	var dragElements = [];
		        if (dd.source.tree) {
		        	dragElements.push(dd.data.node.id);
		        } else if (dd.source.grid) {
		    	    for(var i = 0; i < dd.data.selections.length; i++) {
		    	    	var r = dd.data.selections[i];
		    	    	dragElements.push(r.id);
		    	    }
		    	}
		    	
		    	Catalog.treeitem.move_to({source: dragElements, target: dd.target.id, point: dd.point});
		    	
	        	switch (dd.point) {
	                case "append":
	                	if (dd.source.grid){
	                		dd.target.reload();
	                	} else {
	                		dd.target.appendChild(dd.dropNode);
	                	}
	                	
	                	app.store.load({params: {parent: dd.target.id}});
	                    break;
	                case "above":
	                	if (dd.source.grid){
	                		dd.target.parentNode.reload();
	                	} else {
	                    	dd.target.parentNode.insertBefore(dd.dropNode, dd.target);
	                    }

	                    app.store.load({params: {node_id: dd.target.id}});
	                    break;
	                case "below":
	                	if (dd.source.grid){
	                		dd.target.parentNode.reload();
	                	} else {
	                    	dd.target.parentNode.insertBefore(dd.dropNode, dd.target.nextSibling);
	                    }
	                    
	                    app.store.load({params: {node_id: dd.target.id}});
	                    break;
	                default:
	                    debugger;
	            }

				if (dd.source.grid) {
					var target_node = null;
			    	if ( dd.point == 'below' || dd.point == 'above' ) {
			    		target_node = dd.target.parentNode;
			    	} else {
			    		target_node = dd.target;
			    	}
			    	app.tree.expandPath(target_node.getPath());
			    	//target_node.reload();
			    }
	        }
    	});

		return true;
   	},
   	on_node_select: function(node, event) {
   		if (node.id == 'root') {
   			app.store.load({
   				params: {
   					root: 'root'
   				}
   			});
   		} else if (node.leaf) {
   			app.store.load({
   				params: {
   					id: node.id
   				}
   			});
   		} else {
   			app.store.load({
   				params: {
   					parent: node.id
   				}
   			});
   		}
    }
}


/** ** Catalog app layout building *** */
app.build_layout = function(){
    app.store = new Ext.data.DirectStore({
        storeId: 'DataStore',
        directFn: Catalog.treeitem.objects,
        autoLoad: false,
        remoteSort: false,
        root: 'records',
        fields: app.colmodel
    });
    
	app.addMenu = new Ext.menu.Menu({
		id: 'addMenu',
		items: []
	});
    
    app.gridBar = new Ext.Toolbar({
	    items: [{
	    	text: gettext('Add'),
	    	menu: app.addMenu,
    	},'-',{
	    	text: gettext('Reload'),
	    	handler: function(){
	    		app.store.reload();
	    	}
    	},'-',{
    		text: gettext('Remove'),
    		handler: function(){
    			rows = app.grid.getSelectionModel().getSelections();
    			if (!rows)
    				return false
    			
    			Ext.Msg.confirm(gettext('Confirmation'), gettext('Are you sure you want to remove ' + rows.length + ' items?'), function(button){
    				if (button == 'yes') {
		    			removeObjects = [];
		    			for ( var i = 0; i < rows.length; i++ ) {
		    				removeObjects.push(rows[i].id);
		    				app.store.remove(app.store.getById(rows[i].id));
		    			}
						Catalog.treeitem.remove_objects({objects: removeObjects});
    				}
    			});
    		}
    	}]
    });
    
    app.grid = new Ext.grid.GridPanel({
        store: app.store,
        sm: new Ext.grid.RowSelectionModel({
        	singleSelect:false,
        }),
        cm: new Ext.grid.ColumnModel({
            columns: app.colmodel
        }),
        ddGroup: 'dd',
        maskDisabled : true,
        enableDragDrop: true,
        tbar: app.gridBar,
        listeners: {
            'render': function() {
                // Enable sorting Rows via Drag & Drop
                new Ext.dd.DropTarget(app.grid.getView().mainBody, {
				    ddGroup : 'dd',
				    notifyDrop : app.callbacks.on_grid_drop
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
            text: 'Catalog',
            expanded: true,
            draggable: false,
            nodeType: 'async',
        },
        rootVisible: true,
        ddGroup: 'dd',
        enableDD: true,
        loader: new Ext.tree.TreeLoader({
            directFn: Catalog.treeitem.tree
        }),
        listeners: {
            beforenodedrop: app.callbacks.on_tree_drop,
            click: app.callbacks.on_node_select,
        }
    });
    
    $('#content').html('');
    
    // Hack! 
    $('<div id="wrapper"></div>').prependTo('#container');
    $('#header').appendTo('#wrapper');
    $('.breadcrumbs').appendTo('#wrapper');
    
    app.view = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            margins: '0',
            paddings: '0',
            contentEl: 'wrapper'
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

    /** Hack continue and explanation
    *
    * Since I did not figured how to expand Ext.Panel to screen, I used Ext.Vieport
    * and hacked it to contain all elements that I need in header in 'north' region
    * North region must contain only one element, so I wrapped all of them with jQuery.
    * This can be made with Ext.DomHelper but I tired.
    */ 
    $('#wrapper').parents('.x-panel-body-noheader').css('overflow', 'visible !important');
    $('#wrapper').parents('.x-panel-bwrap').css('overflow', 'visible');

};

/** ** Application initialization part *** */

Ext.onReady(function() {
    Ext.QuickTips.init();
    
    var provider = Ext.Direct.getProvider('catalog_provider');
    provider.on('data', app.direct_data_listener);
    
    Catalog.colmodel.get_col_model();
    Catalog.colmodel.get_models();
});
