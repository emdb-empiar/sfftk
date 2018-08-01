# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(__file__)

SFFTK_VERSION = 'v0.3.1.dev4'

# get the schema version
from sfftk.schema import SFFSegmentation
seg = SFFSegmentation()
EMDB_SFF_VERSION = seg.version
