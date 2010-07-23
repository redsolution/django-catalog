MENU_PROXY_RULES += [
        {
        'name': 'catalog',
        'method': 'children',
        'proxy': 'menuproxy.proxies.MenuProxy',
        'model': 'catalog.models.TreeItem',
    }
]
