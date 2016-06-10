# Environment variable that points to TBB directory:
from os import environ
from os.path import abspath, isdir
from tbselenium.exceptions import TBTestEnvVarError

TBB_PATH = environ.get('TBB_PATH')

if TBB_PATH is None:
    raise TBTestEnvVarError("Environment variable `TBB_PATH` can't be found.")

TBB_PATH = abspath(TBB_PATH)
if not isdir(TBB_PATH):
    raise TBTestEnvVarError("TBB_PATH is not a directory: %s" % TBB_PATH)
