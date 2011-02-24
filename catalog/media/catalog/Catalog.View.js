;Ext.ns('Catalog');
Catalog.View = Ext.extend(Ext.Panel, {
    title: 'Catalog View',
    layout: 'fit',
    initComponent: function() {
        this.items = [{
            xtype: 'grid',
            store: 'DataStore',
            height: 700,
            columns: [
                {
                    xtype: 'numbercolumn',
                    dataIndex: 'id',
                    header: 'id',
                },
                {
                    xtype: 'numbercolumn',
                    dataIndex: 'content_type',
                    header: 'Content Type',
                },
                {
                    xtype: 'datecolumn',
                    dataIndex: 'content_object',
                    header: 'Content object',
                }
            ]
        }];
        Catalog.View.superclass.initComponent.call(this);
    }
});
