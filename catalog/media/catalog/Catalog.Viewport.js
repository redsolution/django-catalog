Ext.ns('Catalog');

Catalog.View = Ext.extend(Ext.Panel, {
    layout: 'border',
    initComponent: function() {
        this.items = [
            {
                region: 'center',
                xtype: 'catalog-grid',
                itemId: 'catalogGrid'
            },
            {
                region: 'west',
                xtype: 'catalog-tree',
                itemId: 'catalogTree'
            },
            {
                xtype: 'container',
                region: 'south',
                width: 100,
                height: 20,
                itemId: 'bottomContainer'
            },
            {
                xtype: 'container',
                region: 'north',
                width: 100,
                height: 30,
                itemId: 'topContainer'
            }
        ];
        Catalog.View.superclass.initComponent.call(this);
    }
});