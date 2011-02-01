Ext.ns('Catalog');

/**** Data Store ****/
Catalog.GridStore = Ext.extend(Ext.data.DirectStore, {
    initComponent: function(){
        var config = {
            xtype: 'directstore',
            storeId: 'CatalogStore',
            directFn: null,
            fields: [
                {
                    name: 'field'
                },
                {
                    name: 'field'
                },
                {
                    name: 'field'
                },
            ]
        };
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        
        Catalog.Grid.superclass.initComponent.call(this);
    }
});
new Catalog.GridStore();

/**** Ctalog grid base class ****/
Catalog.Grid = Ext.extend(Ext.grid.GridPanel, {
    initComponent: function() {
        var config = {
            columns: [
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'string',
                    header: 'Column',
                    sortable: true,
                    width: 100
                },
                {
                    xtype: 'numbercolumn',
                    dataIndex: 'number',
                    header: 'Column',
                    sortable: true,
                    width: 100,
                    align: 'right'
                },
                {
                    xtype: 'datecolumn',
                    dataIndex: 'date',
                    header: 'Column',
                    sortable: true,
                    width: 100
                },
                {
                    xtype: 'booleancolumn',
                    dataIndex: 'bool',
                    header: 'Column',
                    sortable: true,
                    width: 100
                }
            ],
            title: 'Catalog Grid',
            store: 'CatalogGridStore'
        };
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        
        Catalog.Grid.superclass.initComponent.call(this);
    }
});

Ext.reg('catalog-grid', Catalog.Grid);

/**** Tree panel base class ****/

Catalog.Tree = Ext.extend(Ext.tree.TreePanel, {
    initComponent: function() {
        var config = {
            title: 'My Tree'
            ,width: 200
            ,root: {
                text: 'Tree Node'
            }
            ,loader: {
                directFn: null
            }
        };
    // apply config
    Ext.apply(this, Ext.apply(this.initialConfig, config));
    
    Catalog.Tree.superclass.initComponent.call(this);        
    }
});

Ext.reg('catalog-tree', Catalog.Tree);
