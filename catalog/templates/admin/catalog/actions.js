function editItem(id){
	id = String(id).replace('-link', '');
    var win = window.open("/admin/catalog/edit/" + id +
            "/?_popup=1", "EditTreeItemWindow", "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
    win.focus();
}

function edit_related(url, id){
    var win = window.open("/admin/catalog/rel/" + url + '/' + id + "/",
    "RelatedTreeItemWindow", "menubar=no,width=800,height=730,toolbar=no,scrollbars=yes");
    win.focus();
}

function view_on_site(id){
	id = String(id).replace('-link', '');
    var win = window.open("/admin/catalog/view/" + id + "/", "NewWindow", "scrollbars=yes");
    win.focus();
}

/***** move items on drop *****/
function move_items(source_list, target_id, point) {
    var link_regexp = /\d+-link/;
    var objects_to_move = [];

    for (var i=0; i<source_list.length;i++){
        var match = String(source_list[i]).match(link_regexp);
        if (!match) {
            // silently not move links
        	objects_to_move.push(source_list[i]);
        }
    }

    if (objects_to_move.length){
        tree_panel.showMask('Перемещение товара');
    	Ext.Ajax.request({
            url: '/admin/catalog/json/move/',
            timeout: 10000,
            callback: function() {
                grid_panel.reload();
                tree_panel.selModel.selNode.parentNode.reload();
            },
            success: function(response, options){
                tree_panel.hideMask();
            },
            failure: function(response, options){
                tree_panel.hideMask();
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
                source: objects_to_move.join(','),
                target: target_id,
                point: point
            }
        });
    } else {
    	Ext.Msg.alert('Внимание','ссылки переносить нельзя');
    }

}

/********** add items as relations on drop *******/
function add_relations(source_list, target_id, point, url) {
    tree_panel.showMask('Перемещение товара');

    Ext.Ajax.request({
        url: '/admin/catalog/rel/json/' + url + '/add/',
        timeout: 10000,
        callback: function() {
            grid_panel.reload();
            tree_panel.selModel.selNode.parentNode.reload();
        },
        success: function(response, options){
            tree_panel.hideMask();
        },
        failure: function(response, options){
            tree_panel.hideMask();
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
            target: target_id,
            point: point
        }
    });
}


/****** delete items *******/
function delete_items(id_list, sender){
    var link_regexp = /\d+-link/;
    var links_to_delete = [];
    var objects_to_delete = [];
    var children_count = 0;
    var warning_message = '';

    for (var i=0; i<id_list.length;i++){
        var match = String(id_list[i]).match(link_regexp);
        if (match) {
            // we have a link to delete
            links_to_delete.push(id_list[i]);
        } else {
            objects_to_delete.push(id_list[i]);
        }
    }
    
    Ext.Ajax.request({
        url: '/admin/catalog/json/delete_count/',
        success: function(response, options) {
            var data = Ext.util.JSON.decode(response.responseText);
            children_count = data.all - objects_to_delete.length;
            // prepare wraning message
            if (children_count > 0 ){
                warning_message = 'Удаление ' + objects_to_delete.length + 
                ' объектов приведет к удалению ' + children_count + ' дочерних объектов';
                    if (links_to_delete.length > 0 ) {
                        warning_message += 'и ' + links_to_delete.length + 'ссылок. Продолжить?';
                    } else {
                        warning_message += '. Продолжить?';
                    }
            } else {
                warning_message = 'Удалить ' + objects_to_delete.length + ' объектов ';
                    if (links_to_delete.length > 0 ) {
                        warning_message += 'и ' + links_to_delete.length + ' ссылок?';
                    } else {
                        warning_message += '?';
                    }
            }

            var parent_id = tree_panel.selModel.selNode ? tree_panel.selModel.selNode.attributes.id : 'root';

            Ext.Msg.confirm('Внимание!', warning_message,
                function(btn, text){
                    if (btn == 'yes') {
                        Ext.Ajax.request({
                            url: '/admin/catalog/json/delete/',
                            success: function(response, options){
                                if  (sender == 'tree'){
                                    tree_panel.up();
                                    tree_panel.reload();
                                    tree_panel.selModel.selNode.reload();
                                }
                                if (sender == 'grid') {
                                    tree_panel.selModel.selNode.reload();
                                    tree_panel.reload();
                                }
                                
                            },
                            failure: function(response, options){
                                tree_panel.reload();
                                grid_panel.reload();
                            },
                            params: {
                                items: id_list.join(','),
                                parent_id: parent_id 
                            }
                        });
                    }
            });

        },
        params: {
            items: objects_to_delete.join(','),
        }
    });
}

/*********** item context menu ********/
function get_context_menu(type, panel, index) {
	if (index === null){
		var index = null;
	}
    var items = [
    {
        text: 'Посмотреть на сайте',
        icon: '/media/catalog/img/eye.png',
        type: 'all',
        handler: function(){
             node = tree_panel.getSelectionModel().getSelectedNode();
             view_on_site(node.id);
        }
    },{
        text: 'Редактировать',
        icon: '/media/catalog/img/edit.png',
        type: 'all',
        handler: function(){
    		if (panel == 'tree'){
    			var node = tree_panel.getSelectionModel().getSelectedNode();
                editItem(node.id);
    		}
    		if (panel == 'grid'){
    			var node = catalog_store.getAt(index);
    			editItem(node.id);
    		}
            
        }
    },
    {{ chunks.context_menu }}
    {% for relation in relations.itervalues %}
    {
        text: 'Посмотреть связанные {{ relation.menu_name_plural }}',
        type: '{{ relation.target }}',
        handler: function(){
            //TODO:
            edit_related('{{ relation.url }}', tree_panel.selModel.selNode.attributes.id);
        }
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
    ];
    
    // Я решил убрать удаление из контекстного меню таблицы, т.к. не очевидно,
    // что удалять - текущий элемент или все выделенные
    if (panel=='tree'){
        items.push({
            text: 'Удалить',
            icon: '/media/catalog/img/show-no.png',
            type: 'all',
            handler: function(e){
                    node = tree_panel.getSelectionModel().getSelectedNode();
                    delete_items([node.id], 'tree');
                }        
        });
    };


    var menu = []
    for (var i =0; i < items.length; i++) {
        if (items[i]['type'] == type) {
            menu.push(items[i]);
        }
        if (items[i]['type'] == 'all') {
            menu.push(items[i]);
        }
    }
    return new Ext.menu.Menu({items: menu});
}
