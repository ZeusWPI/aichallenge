#!/usr/bin/env python

import os
import sys

INTERP = os.path.expanduser("~/env/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

from pathlib import Path
repo_root = Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

from battlebots.web import app as application
