# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="grandma.django-catalog",
    version="1.1.2",
    description=("Django catalog application for tree-based structures. Integrated with grandma CMS"),
    license="LGPL",
    keywords="django catalog tree admin",

    author="Ivan Gromov",
    author_email="ivan.gromov@redsolution.ru",

    maintainer='Ivan Gromov',
    maintainer_email='ivan.gromov@redsolution.ru',

    url="http://packages.python.org/django-catalog",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
    ],
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
    #ong_description=open('README').read(),
    entry_points={
        'grandma_setup': ['catalog = catalog.grandma_setup', ],
    }
)
