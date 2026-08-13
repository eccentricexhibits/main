#!/usr/bin/env python3
"""Build the Level 1 Lobby event map.  python3 src/build_lobby.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lobby_data
from event_map import build

if __name__ == "__main__":
    build(lobby_data)
