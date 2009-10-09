/********** tree panel element *************/
var drop_source_list = [];
var drop_target = null
var drop_point = 'append';

function grid_to_treenode(item) {
    data = item.data;
    data.id = item.id;
	return new Ext.tree.TreeNode(data);
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
	beforeDrop: function(dropEvent) {
                    // convert data from grid to tree nodes
					if (dropEvent.source['grid']) {
						// drag from grid
						var selections = dropEvent.data.selections;
						var converted_nodes = [];
							for (var i =0; i < selections.length; i++) {
								converted_nodes.push(grid_to_treenode(selections[i]));
							}
						dropEvent.cancel = converted_nodes.length < 1;
                        //select dropped node
                        tree_panel.selModel.select(dropEvent.target);
					}
					// globally make source list
                    var source = dropEvent.source.dragData['grid'] ? converted_nodes : [dropEvent.source.dragData.node];
					drop_source_list = [];
					for (var i=0; i < source.length; i++) {
						if (source[i]['data']) {
							drop_source_list.push(source[i].data.id);
						} else {
							drop_source_list.push(source[i].attributes.id);
						}
					}
                    // globally set drop point
                    drop_point = dropEvent.point;
                    drop_target = dropEvent.target;
                    console.log(drop_source_list, drop_target);

                    // check if sources have all one type
                    one_type = true;
                    function get_type(item) {
                        if (item.attributes) {
                            return item.attributes.type;
                        } else {
                            return item.data.type;
                        }
                    }
                    type = get_type(source[0]);
					for (var i=1; i < source.length; i++) {
                        one_type = one_type && (get_type(source[i]) == type);
                    }
                    if (!one_type) {
                        type = 'none';
                    }

                    menu = get_menu(get_type(drop_target), type);
                    menu.show(dropEvent.target.ui.getAnchor());
                    return false;
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
        //movenode: tree_events.moveNode,
    	beforenodedrop: tree_events.beforeDrop,
        //nodedrop: tree_events.nodeDrop,
		click: tree_events.panelClick,
		//expandnode: tree_events.expandNode,
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


/*********** tree drop menu ***********/
function get_menu(target_type, source_type) {
    var items = [
    {% for relation in relations.itervalues %}
    {
        text: 'Ссылка на {{ relation.menu_name }}',
        target_type: '{{ relation.target }}',
        source_type: '{{ relation.source }}',
        handler: function(arg){
            add_relations(drop_source_list, drop_target.id, drop_point, '{{ relation.url }}');
        }
    },
    {% endfor %}
    {
        text: 'Перенести',
        type: 'all',
        // icon: '/media/catalog/img/eye.png',
        handler: function(arg){
                move_items(drop_source_list, drop_target.id, drop_point);
            }
    }, {
        text: 'Отмена',
        type: 'all'
    }]

    var menu = []
    for (var i =0; i < items.length; i++) {
        if ((items[i]['target_type'] == target_type) & (items[i]['source_type'] == source_type)) {
            menu.push(items[i]);
        }
        if (items[i]['type'] == 'all') {
            menu.push(items[i]);
        }
    }
    return new Ext.menu.Menu({items: menu});
}

