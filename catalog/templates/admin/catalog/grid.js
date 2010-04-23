
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
	                Ext.Msg.alert('Внимание','Выберите раздел для добавления на левой панели');
	                return;
	            }
	            var parentSectionId = tree_panel.selModel.selNode.id;
	            
	            var win = window.open("/admin/{{ model.app }}/{{ model.name }}/add/?parent=" + 
	                    tree_panel.selModel.selNode.id + 
	                    "&_popup=1", "EditTreeItemWindow", 
	                "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
	            win.focus();
	        }
	    }{% if not forloop.last %},{% endif %}
	    {% endfor %}
	    ]
    },
    {{ chunks.grid_bar }}
    {
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
            delete_items(r, 'grid');
		}
    }]
});

var gridStatus = new Ext.ux.StatusBar({
	defaultText: 'Готово',
    id: 'catalog-admin-statusbar'
});

gridStatus.showBusy = function() {
    gridStatus.setText("<img src='/media/catalog/img/ajax-loader.gif' /> Загрузка");
    grid_loading = true;
}

gridStatus.newStatus = function() {
    gridStatus.clearStatus();
    gridStatus.setText(tree_panel.selModel.selNode.attributes.text);
    grid_loading = false;
}

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


var catalog_store = new Ext.data.JsonStore({
    url: '/admin/catalog/json/list/',
    root: 'items',
    fields: [
    {% for field in column_model %}
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


var catalog_col_model = new Ext.grid.ColumnModel({
    defaults: {
        width: 120,
        sortable: true
    },
    columns: [
    {
        id: 'type',
        name: 'type',
        dataIndex: 'type',
        width: 32,
        renderer: renderType
    }
    {% for field in column_model %}
        , {
            id: '{{ field.name }}',
            name: '{{ field.name }}',
            dataIndex: '{{ field.name }}',
            type: '{{ field.type }}',
            {% ifequal field.type 'boolean' %}
            renderer: renderYesNo,
            width: 32,
            {% endifequal %}
            {% ifequal field.name 'name' %}
            width: 300,
            {% endifequal %}
            header: '{{ field.header }}'
        }
    {% endfor %}
]});

/*** events ***/

var grid_events = {
    rowcontextmenu: function(grid, rowIndex, e) {
                        var item = catalog_store.getAt(rowIndex);
                        menu = get_context_menu(get_type(item), 'grid', rowIndex); 
                        menu.show(e.target);
                        e.preventDefault();
                        return false;
        }
};

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
    enableDragDrop: true,
    listeners: {
        rowcontextmenu: grid_events.rowcontextmenu,
//        contextmenu: function(e){return false;}
    }
});

grid_panel.reload = function(){
    catalog_store.reload();
}
