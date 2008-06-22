#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup

setup(
    name = 'TracJoomla',
    version = '0.0.1',
    packages = ['joomla'],

    author = 'Benjamin Berg',
    author_email = 'benjamin@sipsolutions.net',
    description = 'Plugin to integrate Trac with Joomla',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license = 'GPLv2+',
    keywords = 'trac 0.11 plugin joomla',
    #url = 'http://',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['Trac'],
    
    entry_points = {
        'trac.plugins': [
            'joomla.authenticator = joomla.authenticator',
            'joomla.authz_policy = joomla.authz_policy',
        ],
    },
)
