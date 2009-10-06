/********** tree panel element *************/

function grid_to_treenode(item) {
	return new Ext.tree.TreeNode({
		id: item.data.id,
		text: item.data.name
	})
	
}

/********* tree title bar **********/
var treeBar = [{ 
	text: 'Обновить',
	cls: 'x-btn-text-icon',
	icon: '/media/extjs/resources/images/default/grid/refresh.gif',
	handler: function(){
		tree_panel.selModel.selNode.reload();
	}
}];


/******* remembering tree state *********/
new Ext.state.Manager.setProvider(new Ext.state.CookieProvider({
	path: "/",
    expires: new Date(new Date().getTime()+(1000*60*60*24*30)), //30 days
}));

var tree_events = {
	panelClick: function(node, event) {
				    var sn = this.selModel.selNode || {}; // selNode is null on initial selection
				    if (node.id != sn.id) { // ignore clicks on currently selected node
			            Ext.getCmp('catalog-admin-statusbar').showBusy();
			            catalog_store.load({
			                params: {
			                    'node': node.id
			                },
			                callback: function(r, options, success){
			                	Ext.getCmp('catalog-admin-statusbar').clearStatus();
			                	Ext.getCmp('catalog-admin-statusbar').setText(node.attributes.text);
			                }
			            });
			            Ext.state.Manager.set('treestate', node.getPath());
				    }
				},
	expandNode: function(node) {
					
				},
	moveNode: function(tree, node, oldParent, newParent, index) {
				    var post_data = {
				        node: node.id,
				        from: oldParent.id,
				        to: newParent.id,
				        index: index
				    }
				},
	beforeDrop: function(dropEvent) {
					if (dropEvent.source['grid']) {
						// drag from grid
						var selections = dropEvent.data.selections;
						var r = [];
							for (var i =0; i < selections.length; i++) {
								r.push(grid_to_treenode(selections[i]));
							}
						dropEvent.dropNode = r;
						dropEvent.cancel = r.length < 1;
					}
				},
    nodeDrop: function (dropEvent) {
					console.log(dropEvent);
					tree_panel.contextMenuHandler()
					
					
					var source = dropEvent.source.dragData['grid'] ? dropEvent.source.dragData.selections : [dropEvent.source.dragData.node];
					var source_list = [];
					for (var i=0; i < source.length; i++) {
						if (source[i]['data']) {
							source_list.push(source[i].data.id);
						} else {
							source_list.push(source[i].attributes.id);
						}
					}
					
					tree_panel.showMask('Перемещение товара');

				    Ext.Ajax.request({
				        url: '/admin/catalog/json/move',
				        timeout: 10000,
				        success: function(response, options){
				        	tree_panel.hideMask()	
				    		grid_panel.reload();
							tree_panel.reload();
							
				        },
				        failure: function(response, options){
				        	tree_panel.hideMask()
				        	if (response.staus == '500') {
				        		Ext.Msg.alert('Ошибка','Ошибка на сервере');
								grid_panel.reload();
								tree_panel.reload();
				        	}
				        	if (response.isTimeout) {
				        		Ext.Msg.alert('Ошибка','Обрыв связи');
				        		window.location.reload();
				        	}
				        },
				        params: {
				        	source: source_list.join(','),
				        	target: dropEvent.target.id,
				        	point: dropEvent.point
				        }
			    	});
				},
    contextMenuHandler: function(node){
                    node.select();
                    contextMenu.show(node.ui.getAnchor());
                }
}

var tree_panel = new Ext.tree.TreePanel({
    title: 'Разделы',
    // size
    height: 100,
    width: 370,
    minSize: 250,
    maxSize: 370,
    margins: '5 0 5 5',
    // layout
    region: 'west',
    // tree options
    collapsible: true,
    useArrows: true,
    autoScroll: true,
    animate: true,
    enableDD: true,
    ddGroup: 'tree',
    containerScroll: true,
    
    // auto create TreeLoader
    dataUrl: '/admin/catalog/json/tree/',
    root: {
        nodeType: 'async',
        text: 'Каталог',
        draggable: false,
        id: 'root'
    },
    tbar: treeBar,
	listeners: {
//		render: treeDropZoneInit,
    	movenode: tree_events.moveNode,
    	beforenodedrop: tree_events.beforeDrop,
    	nodedrop: tree_events.nodeDrop,
		click: tree_events.panelClick,
		expandnode: tree_events.expandNode,
        contextmenu: tree_events.contextMenuHandler
	}

});

tree_panel.reload = function() {
    // expand the tree and grid to saved state
    var treestate = Ext.state.Manager.get('treestate');
    if (treestate) {
    	tree_panel.selectPath(treestate);
    	var treestate = Ext.state.Manager.get('treestate');
    	catalog_store.load({
    		params: {node: treestate.split('/').reverse()[0]} 
    	});
    } else
        tree_panel.getRootNode().expand();	
}

tree_panel.showMask = function(message) {
    target = Ext.get(this.id);
    mask = new Ext.LoadMask(target, {
        msg: message
    });
    mask.show();
}

tree_panel.hideMask = function () {
	target = Ext.get(this.id);
	mask = new Ext.LoadMask(target);
	mask.hide();
}


/********** tree context menu ******/
var contextMenu = new Ext.menu.Menu ({
    items: [{
        text: 'Посмотреть на сайте',
        icon: '/media/catalog/img/eye.png',
        handler: function(){
                node = tree_panel.getSelectionModel().getSelectedNode();
                view_on_site(node.id);
            }
    },{
        text: 'Редактировать',
        icon: '/media/catalog/img/edit.png',
        handler: function(){
                node = tree_panel.getSelectionModel().getSelectedNode();
                editItem(node.id);
            }
    },{
        text: 'Связи',
        icon: '/media/catalog/img/link.png',
        handler: function(){
                node = tree_panel.getSelectionModel().getSelectedNode();
                edit_related(node.id);
            }
    },{
        text: 'Удалить',
        icon: '/media/catalog/img/show-no.png',
        handler: function(){
                node = tree_panel.getSelectionModel().getSelectedNode();
                deleteItems([node.id]);
                tree_panel.reload();
            }
    }]
});
