#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

extensions = ['sphinxcontrib.doxylink']

doxylink = {
    'my_lib': (os.path.abspath('./my_lib.tag'), 'https://examples.com/'),
}

master_doc = 'index'
