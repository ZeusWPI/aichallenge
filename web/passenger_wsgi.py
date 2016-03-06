#!/usr/bin/env python

import sys
import os

INTERP = os.path.expanduser("~/env/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.path.dirname(os.getcwd()))

from web import app as application
