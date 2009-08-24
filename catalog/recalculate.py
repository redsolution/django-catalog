from django.db import connection
from django.db.transaction import commit_unless_managed

def children_mptt(model, id=None):
    if id is None:
        condition = 'is NULL'
    else:
        condition = '= %s'
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM "%(table)s" WHERE "%(parent)s" %(condition)s;' 
        % {
            'table': model._meta.db_table, 
            'parent': model._meta.get_field(model._meta.parent_attr).column,
            'condition': condition,
        }, [id])
    result = [row[0] for row in cursor.fetchall()]
    commit_unless_managed()
    return result

def recalculate_mptt(model, id=None, left=1, level=0, tree=1):
    if id is None:
        for index, item_id in enumerate(children_mptt(model, id)):
            recalculate_mptt(model, item_id, 1, 0, index + 1)
        return
    point = left
    for item_id in children_mptt(model, id):
        point = recalculate_mptt(model, item_id, point + 1, level + 1, tree)
    right = point + 1
    cursor = connection.cursor()
    cursor.execute(('UPDATE "%(table)s" ' +
        'SET "lft" = %%s, "rght" = %%s, "tree_id" = %%s, "level" = %%s ' + 
        'WHERE id = %%s;') % {'table': model._meta.db_table}, 
        [left, right, tree, level, id])
    commit_unless_managed()
    return right
