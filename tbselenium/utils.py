import sqlite3
import tempfile
import tbselenium.common as cm
from os import environ
from os.path import dirname, isfile, join
from tbselenium.exceptions import StemLaunchError
from selenium.webdriver.common.utils import is_connectable

try:  # only needed for tests
    from pyvirtualdisplay import Display
except ImportError:
    pass

try:  # only needed for tests and examples
    from stem.process import launch_tor_with_config
except ImportError:
    pass

# Default dimensions for the virtual display
DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800


def start_xvfb(win_width=DEFAULT_XVFB_WIN_W,
               win_height=DEFAULT_XVFB_WIN_H):
    """Start and return virtual display using XVFB."""
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    """Stop the given virtual display."""
    if xvfb_display:
        xvfb_display.stop()


def is_busy(port_no):
    """Return True if port is already in use."""
    return is_connectable(port_no)


def prepend_to_env_var(env_var, new_value):
    """Add the given value to the beginning of the environment var."""
    if environ.get(env_var, None):
        if new_value not in environ[env_var].split(':'):
            environ[env_var] = "%s:%s" % (new_value, environ[env_var])
    else:
        environ[env_var] = new_value


def read_file(file_path, mode='rU'):
    """Read and return file content."""
    with open(file_path, mode) as f:
        content = f.read()
    return content


def launch_tbb_tor_with_stem(tbb_path=None, torrc=None, tor_binary=None):
    """Launch the Tor binary in tbb_path using Stem."""
    if not (tor_binary or tbb_path):
        raise StemLaunchError("Either pass tbb_path or tor_binary")
    if not tor_binary and tbb_path:
        tor_binary = join(tbb_path, cm.DEFAULT_TOR_BINARY_PATH)
    if not isfile(tor_binary):
        raise StemLaunchError("Invalid Tor binary")

    prepend_to_env_var("LD_LIBRARY_PATH", dirname(tor_binary))
    temp_data_dir = tempfile.mkdtemp()
    if torrc is None:
        torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
                 'SOCKSPort': str(cm.STEM_SOCKS_PORT),
                 'DataDirectory': temp_data_dir}

    return launch_tor_with_config(config=torrc, tor_cmd=tor_binary)


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
