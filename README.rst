================
Django-catalog
================

Application allows to organize objects in tree hierarhy.

This Documentation is poor for now, but it contains instructions 
how to set up application with default settings. 

Download & Install:
--------------------

**Download**

#) From python package index:::

    pip install djang-catalog

#) From github:::

    pip install -e git://github.com/redsolution/django-catalog.git@2.0.0#egg=Django-catalog

**Quick install**

#) Include applications into ``INSTALLED_APPS``::

    INSTALLED_APPS += [
    ...
    'mptt',
    'catalog',
    'catalog.contrib.defaults',
    ...
    ]    

#) Include catalog in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^catalog/', include('catalog.urls.by_slug')),
    )

#) Run ``manage.py syncdb``

For more complicated installation options look into documentation.

Features
---------

* Nice admin interface with drag-n-grop manipulations.
* Generic model relationship architechture (any model can be included in catalog tree)
* Useful templatetags library
* Hightly customizable


Screenshot:

|catalog-admin|

.. |catalog-admin|  image:: http://github.com/redsolution/django-catalog/raw/2.0.0/docs/admin-screenshot.png


Redsolution CMS classifiers:
----------------------------

`Content plugins`_

.. _`Content plugins`: http://www.redsolutioncms.org/classifiers/content
