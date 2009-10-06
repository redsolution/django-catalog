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