{
    text: 'Отображать',
    icon: '/media/catalog/img/eye--plus.png',
    menu: [{
        text: 'Да',
        icon: '/media/catalog/img/show-yes.png',
        handler: function(){
            var selections = grid_panel.selModel.getSelections();
            var r = [];
            for (var i=0; i < selections.length; i++) {
                r.push(selections[i].id);
            }
            console.log('visible', r);
            Ext.Ajax.request({
                url: '/defaults/visible/',
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
                r.push(selections[i].id);
                }
            Ext.Ajax.request({
                url: '/defaults/visible/',
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
},