Ext.BLANK_IMAGE_URL = '/media/extjs/resources/images/default/s.gif';
Ext.MessageBox.buttonText.yes = "Да";
Ext.MessageBox.buttonText.no = "Нет";

/****** delte items *******/
function deleteItems(id_list){
    Ext.Ajax.request({
        url: '/admin/catalog/json/count/delete',
        success: function(response, options){
            var data = Ext.util.JSON.decode(response.responseText);
            Ext.Msg.confirm('Внимание!', 'Удаление ' + data.items + 
            ' элементов повлечет удаление ' + data.all + ' дочерних элементов. Удалить?',
                function(btn, text){
                    if (btn == 'yes') {
                        Ext.Ajax.request({
                            url: '/admin/catalog/json/delete',
                            success: function(response, options){
                                grid_panel.reload();
                            },
                            failure: function(response, options){
                                grid_panel.reload();
                            },
                            params: {
                                items: id_list.join(','),
                            }
                        });
                    }
            });
        },
        params: {
            items: id_list.join(','),
        }
    });
}

function editItem(id){
    var win = window.open("/admin/catalog/edititem/" + id +
            "/?_popup=1", "EditTreeItemWindow", "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
    win.focus();
}

function edit_related(id){
    var win = window.open("/admin/catalog/relations/" + id +
            "/?_popup=1", "RelatedTreeItemWindow", "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
    win.focus();
}

function view_on_site(id){
    var win = window.open("/admin/catalog/view/" + id + "/", "NewWindow", "scrollbars=yes");
    win.focus();
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

/********** tree panel *************/
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
				        if (node.id != 'root') {
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
					var source = dropEvent.source.dragData['grid'] ? dropEvent.source.dragData.selections : [dropEvent.source.dragData.node];
					var source_list = [];
					for (var i=0; i < source.length; i++) {
						if (source[i]['data']) {
							source_list.push(source[i].data.id);
						} else {
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
    	icon: '/media/extjs/resources/images/default/grid/refresh.gif',
    	handler: function(){
    		catalog_store.reload();
    	}
    },{
    	text: 'Добавить',
    	icon: '/media/extjs/resources/images/default/tree/drop-add.gif',
    	menu: [{
	        text: 'Добавить раздел',
	    	cls: 'x-btn-text-icon',
	    	icon: '/media/catalog/img/folder.png',
	    	handler: function(){
	            if (tree_panel.selModel.selNode == null) {
	                return;
	            }
	            var parentSectionId = tree_panel.selModel.selNode.id;
	            
	            var win = window.open("/admin/catalog/newsection?parent=" + 
	                    tree_panel.selModel.selNode.id + 
	                    "&_popup=1", "EditTreeItemWindow", 
	                "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	            win.focus();
	        }
	    },{
	        text: 'Добавить товар',
	    	cls: 'x-btn-text-icon',
	    	icon: '/media/catalog/img/full_page.png',
	    	handler: function(){
	            if (tree_panel.selModel.selNode == null) {
	                return;
	            }
	            var parentSectionId = tree_panel.selModel.selNode.id;
	            
	            var win = window.open("/admin/catalog/newitem?parent=" + 
	                    tree_panel.selModel.selNode.id + 
	                    "&_popup=1", "EditTreeItemWindow", 
	                "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	            win.focus();
	        }
	    },{
	        text: 'Добавить метатовар',
	    	cls: 'x-btn-text-icon',
	    	icon: '/media/catalog/img/folder_full.png',
	    	handler: function(){
	            if (tree_panel.selModel.selNode == null) {
	                return;
	            }
	            var parentSectionId = tree_panel.selModel.selNode.id;
	            
	            var win = window.open("/admin/catalog/newmetaitem?parent=" + 
	                    tree_panel.selModel.selNode.id + 
	                    "&_popup=1", "EditTreeItemWindow", 
	                "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	            win.focus();
	        }
	    }]
    },{
    	text: 'Отображать',
    	icon: '/media/catalog/img/eye--plus.png',
    	menu: [{
    		text: 'Да',
    		icon: '/media/catalog/img/show-yes.png',
    		handler: function(){
    			var selections = grid_panel.selModel.getSelections();
				var r = [];
				for (var i=0; i < selections.length; i++) {
					r.push(selections[i].data.id);
					}
			    Ext.Ajax.request({
			        url: '/admin/catalog/json/visible',
			        success: function(response, options){
						grid_panel.reload();
			        },
			        failure: function(response, options){
						grid_panel.reload();
			        },
			        params: {
			        	items: r.join(','),
			        	visible: 1
			        }
			    });
			}
    	},{
    		text: 'Нет',
    		icon: '/media/catalog/img/show-no.png',
    		handler: function(){
				var selections = grid_panel.selModel.getSelections();
				var r = [];
				for (var i=0; i < selections.length; i++) {
					r.push(selections[i].data.id);
					}
			    Ext.Ajax.request({
			        url: '/admin/catalog/json/visible',
			        success: function(response, options){
						grid_panel.reload();
			        },
			        failure: function(response, options){
						grid_panel.reload();
			        },
			        params: {
			        	items: r.join(','),
			        	visible: 0
			        }
			    });
			}
    	}]
    },{
		xtype: 'tbfill'
	},{
		text: 'Удалить',
		icon: '/media/catalog/img/show-no.png',
		handler: function(){
			var selections = grid_panel.selModel.getSelections();
			var r = [];
			for (var i=0; i < selections.length; i++) {
				r.push(selections[i].data.id);
				}
            deleteItems(r);
		}
    }]
});

var gridStatus = new Ext.ux.StatusBar({
	defaultText: 'Готово',
    id: 'catalog-admin-statusbar'
});

/********** items grid panel *************/

function renderYesNo(value){
    if (value) 
        return '<div class="show-yes"></div>'
    else 
        return '<div class="show-no"></div>'
}

function renderType(value){
	if (value == 'section')
		return '<div class="section"></div>'
	if (value == 'metaitem')
		return '<div class="metaitem"></div>'		
	if (value == 'item')
		return '<div class="item"></div>'
	if (value == 'link')
		return '<div class="link"></div>'
}

function renderItemOnly(value, metaData, record) {
	if (record.data.type == 'item') 
		return value;
	else 
		return '&nbsp;'
}

var catalog_store = new Ext.data.JsonStore({
    url: '/admin/catalog/json/list',
    root: 'items',
    fields: ['type', 'itemid', 'id', 'name', 'type',
    {
    	name: 'seo_title',
    	type: 'boolean'
    }, {
        name: 'price',
        type: 'int'
    }, {
        name: 'quantity',
        type: 'int'
    }, {
        name: 'seo_keywords',
        type: 'boolean'
    }, {
        name: 'seo_description',
        type: 'boolean'
    }, {
        name: 'show',
        type: 'boolean'
    }, {
        name: 'has_image',
        type: 'boolean'
    }, {
        name: 'has_description',
        type: 'boolean'
    }]
});

var catalog_col_model = new Ext.grid.ColumnModel([{
	id: 'type',
	dataIndex: 'type',
	width: 50,
	renderer: renderType
},{
    id: 'name',
    header: 'Наименование',
    dataIndex: 'name',
    width: 300
}, {
    name: 'price',
    dataIndex: 'price',
    header: 'Цена',
    type: 'int',
    renderer: renderItemOnly
}, {
    name: 'quantity',
    dataIndex: 'quantity',
    header: 'Остаток',
    type: 'int',
    renderer: renderItemOnly
}, {
	id: 'seo_title',
	header: '&nbsp;',
	dataIndex: 'seo_title',
	width: 50,
    renderer: renderYesNo
}, {
	id: 'seo_keywords',
	header: '&nbsp;',
	dataIndex: 'seo_keywords',
	width: 50,
    renderer: renderYesNo
}, {
	id: 'seo_description',
	header: '&nbsp;',
	dataIndex: 'seo_description',
	width: 50,
    renderer: renderYesNo
}, {
	id: 'has_image',
	header: 'IMG',
	dataIndex: 'has_image',
	width: 50,
    renderer: renderYesNo
}, {
	id: 'has_description',
	header: 'DSC',
	dataIndex: 'has_description',
	width: 50,
    renderer: renderYesNo
}, {
	id: 'show',
    header: '&nbsp;',
    dataIndex: 'show',
    width: 50,
    renderer: renderYesNo
}]);

var grid_panel = new Ext.grid.GridPanel({
    //  look
    title: 'Содержимое',
    selModel: new Ext.grid.RowSelectionModel(),
    fields: ['name', 'show'],
//    viewConfig: {forceFit: true},
    //  data
    cm: catalog_col_model,
    ds: catalog_store,
    ddGroup: 'tree',
    tbar: gridBar,
    bbar: gridStatus,
    enableDragDrop: true
});

/*** events ***/

grid_panel.on('rowdblclick', function(grid, rowIndex, e){
	var item = grid.store.getAt(rowIndex);
    editItem(grid.store.getAt(rowIndex).get('id'));
    return false;
});


grid_panel.reload = function(){
    catalog_store.reload();
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
            layout: 'fit',
            border: false,
            margins: '5 5 5 5',
            items: grid_panel
        }]
    });
	tree_panel.reload();

});

function dismissAddAnotherPopup(win, newId, newRepr) {
    win.close();
	grid_panel.reload();
    tree_panel.reload();
}

function dismissRelatedLookupPopup(win, chosenId) {
    win.close();
	grid_panel.reload();
    tree_panel.reload();
}
