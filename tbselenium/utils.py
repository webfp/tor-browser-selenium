import sqlite3
import tempfile
import tbselenium.common as cm
from os import walk, environ
from os.path import join, getmtime, dirname, isfile
import fnmatch
from tbselenium.exceptions import StemLaunchError

try:  # only needed for tests
    from pyvirtualdisplay import Display
except ImportError:
    pass

try:  # only needed for tests and examples
    from stem.process import launch_tor_with_config
except ImportError:
    pass


def modify_env_var(env_var, value, operation="prepend"):
    existing_value = environ.get(env_var, '')
    if operation == "prepend":
        new_env_var = "%s:%s" % (value, existing_value)
    elif operation == "append":
        new_env_var = "%s:%s" % (existing_value, value)
    elif operation == "set":
        new_env_var = value
    environ[env_var] = new_env_var


def launch_tbb_tor_with_stem(tbb_path=None, torrc=None, tor_binary=None):
    if not (tor_binary or tbb_path):
        raise StemLaunchError("Either pass tbb_path or tor_binary")
    if not tor_binary and tbb_path:
        tor_binary = join(tbb_path, cm.DEFAULT_TOR_BINARY_PATH)
    if not isfile(tor_binary):
        raise StemLaunchError("Invalid Tor binary")
    modify_env_var("LD_LIBRARY_PATH", dirname(tor_binary))
    temp_data_dir = tempfile.mkdtemp()
    if torrc is None:
        torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
                 'SOCKSPort': str(cm.STEM_SOCKS_PORT),
                 'DataDirectory': temp_data_dir}

    return launch_tor_with_config(config=torrc, tor_cmd=tor_binary)


def get_dir_mtime(dir_path):
    """Get the last modified time of a directory."""
    return getmtime(dir_path)


def gen_find_files(dir_path, pattern="*"):
    """Return filenames that matches the given pattern under a given dir
    http://www.dabeaz.com/generators/
    """
    for path, _, filelist in walk(dir_path):
        for name in fnmatch.filter(filelist, pattern):
            yield join(path, name)


def read_file(file_path, mode='rU'):
    """Read and return file content."""
    with open(file_path, mode) as f:
        content = f.read()
    return content


# Default size for the virtual display
DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800


def start_xvfb(win_width=DEFAULT_XVFB_WIN_W,
               win_height=DEFAULT_XVFB_WIN_H):
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    if xvfb_display:
        xvfb_display.stop()


def add_canvas_permission(profile_path, canvas_allowed_hosts):
    """Create a permission db (permissions.sqlite) and add
    exceptions for the canvas image extraction for the given domains.
    If we don't add permissions, screenshots taken by TBB < 4.5a3 will be
    blank images due to the canvas fingerprinting defense in the Tor
    Browser.

    Canvas permission is only needed for TBB < 4.5a3.

    With TBB versions >= 4.5a3, chrome scripts are exempted from the
    canvas permission, so Selenium code that grabs the canvas image (which
    should appear as a chrome script) does not require a separate
    permission.

    See, https://trac.torproject.org/projects/tor/ticket/13439
    """
    connect_to_db = sqlite3.connect
    perm_db = connect_to_db(join(profile_path, "permissions.sqlite"))
    cursor = perm_db.cursor()
    # http://mxr.mozilla.org/mozilla-esr31/source/build/automation.py.in
    cursor.execute("PRAGMA user_version=3")
    cursor.execute("""CREATE TABLE IF NOT EXISTS moz_hosts (
      id INTEGER PRIMARY KEY,
      host TEXT,
      type TEXT,
      permission INTEGER,
      expireType INTEGER,
      expireTime INTEGER,
      appId INTEGER,
      isInBrowserElement INTEGER)""")
    for host in canvas_allowed_hosts:
        if host:
            qry = """INSERT INTO 'moz_hosts'
            VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % host
            cursor.execute(qry)
    perm_db.commit()
    cursor.close()
