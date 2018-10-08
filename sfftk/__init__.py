# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(__file__)

SFFTK_VERSION = 'v0.3.1.dev6'

# get the schema version
"""
We add sfftk/schema to the library path to prevent running __init__ on import.
The long-term solution is to move schema/__init__.py to schema/api.py
"""
import sys
sys.path.append('sfftk/schema')
from emdb_sff import segmentation
__seg = segmentation()

EMDB_SFF_VERSION = __seg.schemaVersion
