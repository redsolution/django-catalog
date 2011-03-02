from catalog.models import TreeItem
from django.utils import simplejson
from extdirect.django import ExtDirectStore
from extdirect.django.decorators import remoting
from extdirect.django.providers import ExtRemotingProvider

provider = ExtRemotingProvider(namespace='Catalog', url='/admin/catalog/treeitem/direct/router/')

@remoting(provider, action='treeitem', len=1)
def objects(request):
    data = request.extdirect_post_data[0]
    items = ExtDirectStore(TreeItem)
    return items.query(**data)

@remoting(provider, action='treeitem', len=1)
def tree(request):
    node = request.extdirect_post_data[0]
    if node == 'root':
        node = None
    children = TreeItem.objects.filter(parent=node)
    data = []
    for item in children:
        data.append({
            'leaf': bool(item.children.all().count() == 0),
            'id': item.id,
            'text': unicode(item.content_object),
        })
    
    return simplejson.dumps(data)
