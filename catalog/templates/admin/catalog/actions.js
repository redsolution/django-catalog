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

function move_items(source_list, target_id, point) {
    tree_panel.showMask('Перемещение товара');

    Ext.Ajax.request({
        url: '/admin/catalog/json/move',
        timeout: 10000,
        success: function(response, options){
            tree_panel.hideMask();
            grid_panel.reload();
            tree_panel.reload();
            
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