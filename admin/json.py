from django.http import HttpResponse, HttpResponseServerError
from catalog.models import Section, Item, TreeItem
from django.contrib.auth.decorators import permission_required
from django.utils import simplejson


@permission_required('catalog.add_section', login_url='/admin/')
def tree(request):
    tree = []
    if request.method == 'POST':
        parent = request.REQUEST.get('node', 'root')
        content = get_content(parent)
        
        for section in content['sections']:
            tree.append({'text': section.tree.name,
                         'id': '%d' % section.tree.id,
                         'cls': 'folder',
                         })
        for metaitem in content['metaitems']:
            tree.append({'text': metaitem.tree.name,
                         'id': '%d' % metaitem.tree.id,
                         'cls': 'folder',
                         })
        for item in content['items']:
            tree.append({'text': item.tree.name,
                         'id': '%d' % item.tree.id,
                         'leaf': 'true',
                         'cls': 'leaf',
                         })
    return HttpResponse(simplejson.encode(tree))


@permission_required('catalog.change_section', login_url='/admin/')
def list(request):
    grid = []
    if request.method == 'POST':
        parent = request.REQUEST.get('node', 'root')
        content = get_content(parent)

        for section in content['sections']:
            grid.append({'name': section.tree.name,
                         'id': '%d' % section.tree.id,
                         'cls': 'folder',
                         'type': 'section',
                         'itemid': section.id,
                         })
        for metaitem in content['metaitems']:
            grid.append({'name': metaitem.tree.name,
                         'id': '%d' % metaitem.tree.id,
                         'cls': 'folder',
                         'type': 'metaitem',
                         'itemid': metaitem.id,
                         })
        for item in content['items']:
            grid.append({'name': item.tree.name,
                         'id': '%d' % item.tree.id,
                         'cls': 'leaf',
                         'type': 'item',
                         'itemid': item.id,
                         })
    return HttpResponse(simplejson.encode({'items': grid}))

# moving tree items

def get_tree_item(node):
    if node == 'root':
        item = None
    else:
        try:
            item = TreeItem.objects.get(id=int(node))
        except TreeItem.DoesNotExist, ValueError:
            item = None
    return item

def get_target_and_position(parent, this, index):
    '''
    Returns target and positions for mptt
    (target, position) = get_target_and_position(parent_section, index)
    '''
    if parent:
        siblings = parent.get_children().exclude(id=this.id)
    else:
        siblings = TreeItem.objects.filter(
            parent=None).exclude(id=this.id)

    if siblings:
        try:
            target = siblings[index]
            position = 'left'
        except IndexError:
            target = siblings.order_by('-lft')[0]  # last element
            position = 'right'
    else:
        # if section is empty - insert first_child
        target = parent
        position = 'first-child'
    return (target, position)

def may_move(node, parent):
    move_matrix = {
        'item': ['section', 'metaitem'],
        'metaitem': ['section'],
        'section': ['section'],
        }
    if parent is None:
        return True
    elif parent.get_type() in move_matrix[node.get_type()]:
        return True
    else:
        return False

def move_node(request):
    if request.method == 'POST':
        this_section = get_tree_item(request.REQUEST.get('node', None))
        new_parent = get_tree_item(request.REQUEST.get('to', None))
        index = int(request.REQUEST.get('index', 0))
    
        if may_move(this_section, new_parent):
            (target, position) = get_target_and_position(new_parent, this_section, index)
            this_section.move_to(target, position)
            return HttpResponse('OK')
        else:
            return HttpResponseServerError('Can not move')
