# Environment variable that points to TBB directory:
from os import environ
TBB_PATH = environ.get('TBB_PATH')
if TBB_PATH is None:
    raise RuntimeError("Environment variable `TBB_PATH` with TBB directory not found.")
