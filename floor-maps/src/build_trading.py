#!/usr/bin/env python3
"""Build the Level 2 Trading Floor event map.  python3 src/build_trading.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import trading_data
from event_map import build

if __name__ == "__main__":
    build(trading_data)
