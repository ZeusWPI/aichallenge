#!/usr/bin/env python

import os
import sys
from urllib.parse import unquote

INTERP = os.path.expanduser("~/env/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

from pathlib import Path
repo_root = Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

from battlebots.web import app


def application(environ, start_response):
    environ["PATH_INFO"] = unquote(environ["PATH_INFO"])
    return app(environ, start_response)
