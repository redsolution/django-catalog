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

new Ext.state.Manager.setProvider(new Ext.state.CookieProvider({
	path: "/",
    expires: new Date(new Date().getTime()+(1000*60*60*24*30)), //30 days
}));

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

app.expand_tree = function () {
	var treestate = Ext.state.Manager.get('treestate');
	app.tree.selectPath(treestate, null, function(){
	    app.tree.selModel.selNode.expand();
	});
}

app.grid_open_edit_window = function(grid, rowIndex, colIndex) {
    var win = window.open(
        app.store.getAt(rowIndex).json.url + '?' + Ext.urlEncode({_popup: 1}),
        "",
        "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes"
    );
    win.focus();
}

app.grid_renderYesNo = function(value){
    if (value) 
        return '<div class="show-yes"></div>'
    else 
        return '<div class="show-no"></div>'
}

app.grid_renderType = function(value){
    return '<div class="' + value + '"></div>'
}

app.reload_selected_node = function() {
    // if selected node is leaf, than reload parent node
    var selected_node = app.tree.selModel.getSelectedNode();
    if (selected_node.leaf) {
        selected_node = selected_node.parentNode;
    }
    selected_node.reload();
}

app.after_move = [];

/**** bind server data events to asynchronous handlers ****/ 
app.direct_handlers = {
    on_get_col_model: function(provider, event) {
        app.colmodel = event.result;
        app.colmodel.push({
	    	xtype: 'actioncolumn',
	    	width: 50,
	    	items: [{
	    		icon: __static_media_prefix__ + 'catalog/img/cog_edit.png',
	    		tooltip: gettext('Change'),
	    		handler: app.grid_open_edit_window
	    	},{
	    		icon: __static_media_prefix__ + 'catalog/img/delete.png',
	    		tooltip: gettext('Delete'),
	    		handler: function(grid, rowIndex, colIndex) {
	    			Ext.Msg.confirm(gettext('Confirmation'), gettext('Are you sure you want to remove this item?'), function(button){
	    				if (button == 'yes') {
	    					// remove TreeItem from database
							Catalog.treeitem.remove_objects({objects: [app.store.getAt(rowIndex).json.id]});
							// remove item from store & grid
							app.store.remove(app.store.getById(app.store.getAt(rowIndex).json.id));
							app.reload_selected_node();
	    				}
	    			});
	            }
	    	}]
	    });
        
        /*** Build application layout after column model recieved from server ***/
        app.build_layout();
    },
    direct_data_listener: function(provider, event){
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
        
        if (event.action === 'treeitem' && event.method === 'move_to') {
            for (var i=0; i<app.after_move.length;i++){
                app.after_move[i]();
            }
            app.after_move = [];
        }
    }
};

app.callbacks = {
    on_grid_drop: function(source, e, data) {
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
                app.after_move.push(function(){
                    app.reload_selected_node();
                });
            }
        } else {
            // Drop from tree not supported yet...
            return false;
        }

        Catalog.treeitem.move_to({source: dragElements, target: targetElement.id, point: 'above'})
        
        return false;
    },
    on_tree_drop: function(dd, e, data) {
        
        // Collect drag elements
        var dragElements = [];
        if (dd.source.tree) {
            dragElements.push(dd.data.node.id);
        } else if (dd.source.grid) {
            for(var i = 0; i < dd.data.selections.length; i++) {
                var r = dd.data.selections[i];
                dragElements.push(r.id);
            }
        }
        
        // Do not allow drag object on itself
        if (dd.source.grid && dd.point==='append') {
            for (var i=0; i<dragElements.length;i++){
                if (dragElements[i] === dd.target.id) {
                    return false;
                }
            }
        } else if (dd.source.grid && ( dd.point==='above') || (dd.point === 'below')){
            for (var i=0; i<dragElements.length;i++){
                if (dragElements[i] === dd.target.parentNode.id) {
                    return false;
                }
            }
        }
        
    	// disables the animated repair
    	dd.tree.dragZone.proxy.animRepair = false;
    	
    	// cancels the drag&drop operation
    	dd.cancel = true;
    	
    	// display the modal confirm dialog
    	Ext.Msg.confirm(gettext('Confirmation'), gettext('Are you sure you want to move this item?'), function(button){
    		// the animated repair is enabled again
    		dd.tree.dragZone.proxy.animRepair = true;
    		
	        if (button == 'yes') {
		    	Catalog.treeitem.move_to({source: dragElements, target: dd.target.id, point: dd.point});
		    	// Deferred callback, will be executed one time after server responds
		    	if (dd.source.grid) {
		    	    app.after_move.push(function(){
		    	        for (var i=0; i<dragElements.length;i++){
		    	            var node = app.tree.getNodeById(dragElements[i]);
		    	            if (node){
		    	                node.destroy();
		    	            }
		    	        }
		    	    });
		    	}
		    	
	        	switch (dd.point) {
	                case "append":
	                	if (dd.source.grid){
                	        dd.target.reload(function(){
                	            app.tree.selModel.select(dd.target);
                	            app.store.load({params: {parent: app.tree.selModel.selNode.id}});
                	        });
	                	} else {
	                	    app.tree.selModel.select(dd.target);
	                	    dd.target.appendChild(dd.dropNode);
	                	    dd.target.expand();
	                	    app.store.load({params: {parent: dd.target.id}});
	                	}
	                    
	                	break;
	                case "above":
	                	if (dd.source.grid){
	                	    dd.target.parentNode.reload(function(){
	                	        var targetNode = app.tree.getNodeById(dd.target.id);
	                	        app.tree.selModel.select(targetNode.parentNode);
	                	        app.store.load({params: {parent: app.tree.selModel.selNode.id}});
	                	    });
	                	} else {
	                	    app.tree.selModel.select(dd.target.parentNode);
	                	    dd.target.parentNode.insertBefore(dd.dropNode, dd.target);
	                	    app.store.load({params: {parent: dd.target.id}});
	                	}
	                    
	                    break;
	                case "below":
	                	if (dd.source.grid){
	                	    dd.target.parentNode.reload(function(){
	                	        var targetNode = app.tree.getNodeById(dd.target.id);
                                app.tree.selModel.select(targetNode.parentNode);
                                app.store.load({params: {parent: app.tree.selModel.selNode.id}});
	                	    });
	                	} else {
	                	    app.tree.selModel.select(dd.target.parentNode);
	                	    dd.target.parentNode.insertBefore(dd.dropNode, dd.target.nextSibling);
	                	    app.store.load({params: {parent: dd.target.id}});
	                	}

	                    break;
	                default:
	                    debugger;
	            }
	        }
    	});

		return true;
   	},
   	on_node_select: function(node, event) {
   		if (node === app.tree.root) {
   			app.store.load({
   				params: {
   					parent: 'root'
   				}
   			});
   		} else if (node.leaf) {
   			app.store.load({
   				params: {
   					parent: node.parentNode.id
   				}
   			});
   		} else {
   			app.store.load({
   				params: {
   					parent: node.id
   				}
   			});
   		}
   		
   		Ext.state.Manager.set('treestate', node.getPath());
    },
    tree_panel_reload: function() {
        // expand the tree and grid to saved state
        var treestate = Ext.state.Manager.get('treestate');
        var node_id = 'root';
        if (treestate) {
            node_id = treestate.split('/').reverse()[0];
            app.tree.selectPath(treestate);
            app.store.load({
                params: {parent: node_id} 
            });
        } else {
            app.tree.selModel.select(app.tree.getRootNode());
            app.tree.getRootNode().expand();
            app.store.load({
                params: {parent: node_id} 
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
	    	text: gettext('Refresh'),
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
						app.reload_selected_node();
    				}
    			});
    		}
    	}]
    });
    
    app.treeBar = new Ext.Toolbar({
        items: [{
            text: gettext('Refresh'),
            handler: function(){
                app.tree.root.reload();
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
            },
            'rowdblclick': app.grid_open_edit_window
        },
    });
    
    app.tree = new Ext.tree.TreePanel({
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
        tbar: app.treeBar,
        listeners: {
            beforenodedrop: app.callbacks.on_tree_drop,
            click: app.callbacks.on_node_select,
            afterrender: app.callbacks.tree_panel_reload,
            load: app.expand_tree,
        }
    });
    
    jQuery('#content').html('');
    
    // Hack! 
    jQuery('<div id="wrapper"></div>').prependTo('#container');
    jQuery('#header').appendTo('#wrapper');
    jQuery('.breadcrumbs').appendTo('#wrapper');
    
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
    jQuery('#wrapper').parents('.x-panel-body').css('overflow','visible');
    jQuery('#wrapper').parents('.x-panel-bwrap').css('overflow','visible');
};

/** ** Application initialization part *** */

Ext.onReady(function() {
    Ext.QuickTips.init();
    
    var provider = Ext.Direct.getProvider('catalog_provider');
    provider.on('data', app.direct_handlers.direct_data_listener);
    
    // Fire ExtDirect functions to initialize interface
    Catalog.colmodel.get_col_model();
    Catalog.colmodel.get_models();
});


/********* Django admin site routines ******/
function dismissAddAnotherPopup(win, newId, newRepr) {
    win.close();
    app.tree.selModel.getSelectedNode().reload();
    app.store.reload();
};


