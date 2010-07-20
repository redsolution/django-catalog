Ext.BLANK_IMAGE_URL = '/media/extjs/resources/images/default/s.gif';

function closeandreload(){
	window.opener.location.reload();
	window.close();
}

function save_items(selected, onSuccess) {
    Ext.Ajax.request({
        url: '/admin/catalog/rel/json/{{ m2m.url }}/{{ instance.tree_id }}/save/',
        success: onSuccess,
        params: {
        	items: selected.join(',')
        }
    });
}

var topBar = new Ext.Toolbar({
	items: [{
		text: 'Сохранить',
		cls: 'x-btn-text-icon',
		icon: '/media/catalog/img/save.png',
		handler: function(){
			var selNodes = rel_tree_panel.getChecked();
			var selected = [];
			for (var i = 0; i < selNodes.length; i++){
				selected.push(selNodes[i].id);
			}
			save_items(selected, null);
		}
	},{
		xtype: 'tbfill'
	},{
		text: 'Сохранить и закрыть',
		cls: 'x-btn-text-icon',
		icon: '/media/catalog/img/show-no.png',
		handler: function(){
			var selNodes = rel_tree_panel.getChecked();
			var selected = [];
			for (var i = 0; i < selNodes.length; i++){
				selected.push(selNodes[i].id);
			}

			save_items(selected, closeandreload);
		}
	}]
});

var rel_tree_panel = new Ext.tree.TreePanel({
    title: 'Связанные {{ rel_verbose_name_plural }} ',
    // size
    height: 500,
    margins: '5 0 0 5',
    // tree options
    useArrows: true,
    autoScroll: true,
    animate: true,
    enableDD: false,
    containerScroll: true,
    frame: true,

    // auto create TreeLoader
    dataUrl: '/admin/catalog/rel/json/{{ m2m.url }}/{{ instance.tree_id }}/tree/',

    root: {
        nodeType: 'async',
        text: 'Каталоги',
        id: 'root',
    }

});

/********** binding *************/

Ext.onReady(function(){
    new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            contentEl: 'header-ct',
            border: 0,
    	}, {
        	region: 'center',
            border: false,
            margins: '5 5 0 5',
            layout: 'column',
            tbar: topBar,
            items: [{
            	columnWidth: 1,
            	items: [rel_tree_panel]
            }]
        }]
    });
    rel_tree_panel.getRootNode().expand();	
});
