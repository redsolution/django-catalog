Ext.BLANK_IMAGE_URL = '/media/catalog/extjs/resources/images/default/s.gif';
Ext.MessageBox.buttonText.yes = "Да";
Ext.MessageBox.buttonText.no = "Нет";


/********** tree panel *************/
function grid_to_treenode(item) {
	return new Ext.tree.TreeNode({
		id: item.data.id,
		text: item.data.name
	})
	
}

/********* tree title bar **********/
var treeBar = new Ext.Toolbar({
	items: [{
		text: 'Обновить'
	}]
})


/******* remembering tree state *********/
new Ext.state.Manager.setProvider(new Ext.state.CookieProvider());

var tree_events = {
	panelClick: function(n) {
				    var sn = this.selModel.selNode ||
				    {}; // selNode is null on initial selection
				    if (n.id != sn.id) { // ignore clicks on currently selected node
				        if (n.id != 'root') {
				            Ext.getCmp('catalog-admin-statusbar').showBusy();
				            catalog_store.load({
				                params: {
				                    'node': n.id
				                },
				                callback: function(r, options, success){
				                    Ext.getCmp('catalog-admin-statusbar').clearStatus();
				                }
				            });
				        }
				    }
				},
	expandNode: function(node) {
					console.log('expand', node);
					Ext.state.Manager.set('treestate', node.getPath());
				},
	moveNode: function(tree, node, oldParent, newParent, index) {
					console.log('move node');
				    var post_data = {
				        node: node.id,
				        from: oldParent.id,
				        to: newParent.id,
				        index: index
				    }
				},
	beforeDrop: function(dropEvent) {
					console.log('before drop', dropEvent);
					
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
//					console.log('node drop', dropEvent);
					
					var source = dropEvent.source.dragData['grid'] ? dropEvent.source.dragData.selections : [dropEvent.source.dragData.node];
					var source_list = [];
					for (var i=0; i < source.length; i++) {
						if (source[i]['data']) {
							source_list.push(source[i].data.id);
						} else {
							console.log('source[i]:', source[i]);
							source_list.push(source[i].attributes.id);
						}
					}
					
				    Ext.Ajax.request({
				        url: '/admin/catalog/json/move',
				        success: function(response, options){
							grid_panel.reload();
				        },
				        failure: function(response, options){
							grid_panel.reload();
				        },
				        params: {
				        	source: source_list.join(','),
				        	target: dropEvent.target.id,
				        	point: dropEvent.point
				        }
			    	});
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
    dataUrl: '/admin/catalog/json/tree',
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
		expandnode: tree_events.expandNode
	}

});

/********** menu panel *************/

function showAddAnotherPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^add_/, '');
    name = id_to_windowname(name);
    href = triggeringLink.href
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

var gridBar = new Ext.Toolbar({
    items: [{
    	text: 'Обновить',
    	cls: 'x-btn-text-icon',
    	icon: '/media/catalog/extjs/resources/images/default/grid/refresh.gif',
    	handler: function(){
    		catalog_store.reload();
    	}
    	
    },{
        text: 'Добавить раздел',
    	cls: 'x-btn-text-icon',
    	icon: '/media/catalog/extjs/resources/images/default/tree/drop-add.gif',
    	handler: function(){
            if (tree_panel.selModel.selNode == null) {
                return;
            }
            var parentSectionId = tree_panel.selModel.selNode.id;
            
            var win = window.open("/admin/catalog/new?parent=" + 
                    tree_panel.selModel.selNode.id + 
                    "&_popup=1", "EditTreeItemWindow", 
                "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
            win.focus();
        }
    }]
});

var gridStatus = new Ext.StatusBar({
	defaultText: 'Готово',
    id: 'catalog-admin-statusbar'
});

/********** items grid panel *************/

function renderShown(value){
    if (value) 
        return '<div class="show-yes"></div>'
    else 
        return '<div class="show-no"></div>'
}

var catalog_store = new Ext.data.JsonStore({
    url: '/admin/catalog/json/list',
    root: 'items',
    fields: ['type', 'itemid', 'id', 'name', 'type',
             'seo_title', 
    {
        name: 'seo_keywords',
        type: 'boolean'
    }, {
        name: 'show',
        type: 'boolean'
    }]
});

var catalog_col_model = new Ext.grid.ColumnModel([{
    id: 'name',
    header: 'Наименование',
    dataIndex: 'name',
    width: 220
}, {
    id: 'show',
    header: 'Отображать',
    dataIndex: 'show',
    width: 50,
    renderer: renderShown
}]);

var grid_panel = new Ext.grid.GridPanel({
    //  look
    height: 500,
    title: 'Содержимое',
    selModel: new Ext.grid.RowSelectionModel(),
    fields: ['name', 'show'],
    //  data
//    cm: catalog_col_model,
    columns: [
              {header: 'Name', dataIndex: 'name'},
              {header: 'Show', dataIndex: 'show'},
              {header: 'Type', dataIndex: 'type'}        
    ],
    ds: catalog_store,
    ddGroup: 'tree',
    tbar: gridBar,
    bbar: gridStatus,
    enableDragDrop: true
});

/*** events ***/

grid_panel.on('rowdblclick', function(grid, rowIndex, e){
	var item = grid.store.getAt(rowIndex);
	if (item.get('type') == 'item') { 
		var win = window.open("/admin/catalog/item/" +
				grid.store.getAt(rowIndex).get('itemid') +
				"/?_popup=1", "EditTreeItemWindow", "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	} else {
		var win = window.open("/admin/catalog/section/" + 
				grid.store.getAt(rowIndex).get('itemid') +
				"/?_popup=1", "EditTreeItemWindow", "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	}
    win.focus();
    return false;
});


grid_panel.reload = function(){
	catalog_store.reload();
//    var wasExpanded = tree_panel.selModel.selNode ? tree_panel.selModel.selNode.expanded : 'root' ;
//    tree_panel.loader.load(tree_panel.selModel.selNode);
//    if (wasExpanded) {
//        tree_panel.selModel.selNode.expand();
//    }
}

/********** binding *************/

Ext.onReady(function(){

    new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            contentEl: 'header-ct',
            border: 0,
        }, tree_panel, {
            region: 'center',
            layout: 'anchor',
            border: false,
            margins: '5 5 5 5',
            items: [grid_panel]
        }]
    });
	
    // expand the tree
    var treestate = Ext.state.Manager.get('treestate');
    if (treestate)
    	tree_panel.expandPath(treestate);
    else
    	tree_panel.getRootNode().expand();
});


function dismissAddAnotherPopup(win, newId, newRepr) {
    win.close();
	grid_panel.reload();
}

function dismissRelatedLookupPopup(win, chosenId) {
    win.close();
	grid_panel.reload();
}
