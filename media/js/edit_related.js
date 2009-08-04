Ext.BLANK_IMAGE_URL = '/media/catalog/extjs/resources/images/default/s.gif';

var currentNode = document.location.href.split('/').reverse()[2];

function save_related() {

}

var relatedBar = new Ext.Toolbar({
	items: [{
		text: 'Сохранить и закрыть',
		cls: 'x-btn-text-icon',
		icon: '/media/catalog/images/show-no.png',
		handler: function(){
			var selNodes = related_tree_panel.getChecked();
			var selected = [];
			for (var i = 0; i < selNodes.length; i++){
				selected.push(selNodes[i].id);
			}
		    Ext.Ajax.request({
		        url: '/admin/catalog/json/relative/' + currentNode + '/save/',
		        success: function(response, options){
					window.opener.location.reload();
					window.close();
		    	},
		        params: {
		        	relative: selected.join(','),
		        }
		    });	
		}
	},{
		xtype: 'tbfill'
	},{ 
		text: 'Сохранить',
		cls: 'x-btn-text-icon',
		icon: '/media/catalog/images/save.png',
		handler: function(){
			var selNodes = related_tree_panel.getChecked();
			var selected = [];
			for (var i = 0; i < selNodes.length; i++){
				selected.push(selNodes[i].id);
			}
		    Ext.Ajax.request({
		        url: '/admin/catalog/json/relative/' + currentNode + '/save/',
		        params: {
		        	relative: selected.join(',')
		        }
		    });	
		}
	}]
}); 

var related_tree_panel = new Ext.tree.TreePanel({
    title: 'Связаные товары',
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
    },
    tbar: relatedBar
});


/********** binding *************/

Ext.onReady(function(){
    new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'center',
            border: false,
            margins: '5 5 5 5',
            layout: 'column',
            items: [{
            	columnWidth: 0.5,
            	items: [related_tree_panel]
        	}, {
                columnWidth: 0.5,
                xtype: 'panel',
                html: 'Right panel'
            }]
        }]
    });

});
