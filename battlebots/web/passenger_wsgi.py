#!/usr/bin/env python

import os
import sys

INTERP = os.path.expanduser("~/env/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.path.dirname(os.getcwd()))

