================
django-catalog
================

Application allows to organize objects in tree hierarhy.

This Documentation is poor for now, but it contains instructions 
how to set up application with default settings. 

Install:
--------

1. Download ``django-catalog`` and include it into python path.
 
2. Edit your ``settings.py`` this way: ::

    INSTALLED_APPS += [
        'catalog',
        'catalog.contrib.defaults',
    ]
  
And insert one of this strings into ``urlconf.py``: :: 

    urlpatterns += patterns('', 
        (r'^catalog/', include('catalog.urls.by_id')),
    )

or ::

    urlpatterns += patterns('', 
        (r'^catalog/', include('catalog.urls.by_slug')),
    )

Method ``by_id`` will configure views to display tree items urls like this:
``http://example.com/catalog/my-item-47/``. Where ``my-item`` is object's slug,
and ``47`` is TreeItem id attribute.

Method ``by_slug`` will configure views to display tree items urls like this:
``http://example.com/catalog/item-my-item/``. Where ``my-item`` is object's slug,
and ``item`` is Item models name.

Notice, that when you use method ``by_slug``, every object **MUST** have ``slug`` 
attribute.

Classifiers:
-------------

`Frontpage handlers`_

.. _`Frontpage handlers`: http://www.redsolutioncms.org/classifiers/frontpage