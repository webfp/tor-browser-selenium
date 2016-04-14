# Environment variable that points to TBB directory:
from os import environ
from os.path import abspath, isdir

TBB_PATH = environ.get('TBB_PATH')

if TBB_PATH is None:
    raise RuntimeError("Environment variable `TBB_PATH` cannot be found.")

TBB_PATH = abspath(TBB_PATH)
if not isdir(TBB_PATH):
    raise RuntimeError("`TBB_PATH` is not a directory.")
