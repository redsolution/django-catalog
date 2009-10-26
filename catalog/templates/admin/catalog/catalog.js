Ext.BLANK_IMAGE_URL = '/media/extjs/resources/images/default/s.gif';
Ext.MessageBox.buttonText.yes = "Да";
Ext.MessageBox.buttonText.no = "Нет";
/** globals **/

var drop_source_list = [];
var drop_target = null
var drop_point = 'append';
var catalog_loading = false;

{% include 'admin/catalog/actions.js' %}

{% include 'admin/catalog/tree.js' %}

{% include 'admin/catalog/grid.js' %}

/********** layout *************/
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

/********* Django admin site routines ******/
function dismissAddAnotherPopup(win, newId, newRepr) {

	grid_panel.reload();
	node = tree_panel.selModel.selNode;
	node.reload();
    win.close();
}

function dismissRelatedLookupPopup(win, chosenId) {
	grid_panel.reload();
    tree_panel.reload();
    win.close();
}

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
