
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
        menu: [
        {% for model in models %}
        {
	        text: 'Добавить {{ model.verbose_name }}',
	    	cls: 'x-btn-text-icon',
	    	icon: '/media/catalog/img/folder.png',
	    	handler: function(){
	            if (tree_panel.selModel.selNode == null) {
	                return;
	            }
	            var parentSectionId = tree_panel.selModel.selNode.id;
	            
	            var win = window.open("/admin/catalog/new/{{ model.name }}/?parent=" + 
	                    tree_panel.selModel.selNode.id + 
	                    "&_popup=1", "EditTreeItemWindow", 
	                "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	            win.focus();
	        }
	    }{% if not forloop.last %},{% endif %}
	    {% endfor %}
	    ]
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
				r.push(selections[i].id);
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
    return '<div class="' + value + '"></div>'
}

function renderItemOnly(value, metaData, record) {
	if (record.data.type == 'item') 
		return value;
	else 
		return '&nbsp;'
}

var catalog_store = new Ext.data.JsonStore({
    url: '/admin/catalog/json/list/',
    root: 'items',
    fields: [
    {% for field in column_model.itervalues %}
        {
            name: '{{ field.name }}',
            type: '{{ field.type }}'
        },
    {% endfor %}
    {
        name: 'type',
        type: 'string'
    }
    ]
});

var catalog_col_model = new Ext.grid.ColumnModel([
    {% for field in column_model.itervalues %}
        {
            id: '{{ field.name }}',
            name: '{{ field.name }}',
            dataIndex: '{{ field.name }}',
            type: '{{ field.type }}',
            header: '{{ field.header }}'
            //width: 50,
            //renderer: renderType, renderItemOnly, renderYesNo
        }{% if not forloop.last %},{% endif %}
    {% endfor %}
]);

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
    editItem(grid.store.getAt(rowIndex).id);
    return false;
});


grid_panel.reload = function(){
    catalog_store.reload();
}
