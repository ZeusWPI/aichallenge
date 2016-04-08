#!/usr/bin/env python

import os
import sys

INTERP = os.path.expanduser("~/env/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

from pathlib import Path
from urllib.parse import unquote

repo_root = Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

from battlebots.web import app as application

wsgi_app = application.wsgi_app


def _app(environ, start_response):
    environ["PATH_INFO"] = unquote(environ["PATH_INFO"])
    return wsgi_app(environ, start_response)

application.wsgi_app = _app
