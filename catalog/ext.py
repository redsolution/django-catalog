from catalog.models import TreeItem
from extdirect.django import ExtDirectStore
from extdirect.django.decorators import remoting
from extdirect.django.providers import ExtRemotingProvider

provider = ExtRemotingProvider(namespace='Catalog', url='/admin/catalog/treeitem/direct/router/')

@remoting(provider, action='treeitem', len=1)
def objects(request):
    data = request.extdirect_post_data[0]
    items = ExtDirectStore(TreeItem)
    return items.query(**data)