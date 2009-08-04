Ext.BLANK_IMAGE_URL = '/media/catalog/extjs/resources/images/default/s.gif';

var currentNode = document.location.href.split('/').reverse()[2];

function closeandreload(){
	window.opener.location.reload();
	window.close();
}

function save_relative(selected, onSuccess) {
    Ext.Ajax.request({
        url: '/admin/catalog/json/relative/' + currentNode + '/save/',
        success: onSuccess,
        params: {
        	relative: selected.join(',')
        }
    });
}

function save_sections(selected, onSuccess) {
    Ext.Ajax.request({
        url: '/admin/catalog/json/sections/' + currentNode + '/save/',
        success: onSuccess,
        params: {
        	sections: selected.join(',')
        }
    });
}

var topBar = new Ext.Toolbar({
	items: [{
		text: 'Сохранить',
		cls: 'x-btn-text-icon',
		icon: '/media/catalog/images/save.png',
		handler: function(){
			var selNodes = related_tree_panel.getChecked();
			var rel_selected = [];
			for (var i = 0; i < selNodes.length; i++){
				rel_selected.push(selNodes[i].id);
			}

			selNodes = section_tree_panel.getChecked();
			var sec_selected = [];
			for (var i = 0; i < selNodes.length; i++){
				sec_selected.push(selNodes[i].id);
			}

			save_relative(rel_selected, null);
			save_sections(sec_selected, null);
		}
	},{
		xtype: 'tbfill'
	},{
		text: 'Сохранить и закрыть',
		cls: 'x-btn-text-icon',
		icon: '/media/catalog/images/show-no.png',
		handler: function(){
			var selNodes = related_tree_panel.getChecked();
			var rel_selected = [];
			for (var i = 0; i < selNodes.length; i++){
				rel_selected.push(selNodes[i].id);
			}

			selNodes = section_tree_panel.getChecked();
			var sec_selected = [];
			for (var i = 0; i < selNodes.length; i++){
				sec_selected.push(selNodes[i].id);
			}

			save_relative(rel_selected, closeandreload);
			save_sections(sec_selected, closeandreload);
		}
	}]
});

var related_tree_panel = new Ext.tree.TreePanel({
    title: 'Связанные товары',
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
    dataUrl: '/admin/catalog/json/relative/' + currentNode + '/',

    root: {
        nodeType: 'async',
        text: 'Каталог',
        id: 'root',
    }

});

var section_tree_panel = new Ext.tree.TreePanel({
    title: 'Дополнительные разделы',
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
    dataUrl: '/admin/catalog/json/sections/' + currentNode + '/',

    root: {
        nodeType: 'async',
        text: 'Каталог',
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
            	columnWidth: 0.49,
            	items: [related_tree_panel]
            }, {
            	xtype: 'panel',
            	columnWidth: 0.02,
            	frame: true,
            	height: 500
            },{
                columnWidth: 0.49,
                items: [section_tree_panel]
            }]
        }]
    });

});
