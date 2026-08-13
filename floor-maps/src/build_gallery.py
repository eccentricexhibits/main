#!/usr/bin/env python3
"""Build the Level 3 Gallery event map.  python3 src/build_gallery.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gallery_data
from event_map import build

if __name__ == "__main__":
    build(gallery_data)
