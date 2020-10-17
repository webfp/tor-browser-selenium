import tempfile
import tbselenium.common as cm
from os import environ
from os.path import dirname, isfile, join
from tbselenium.exceptions import StemLaunchError
from selenium.webdriver.common.utils import is_connectable
from time import sleep
import json

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

# Security slider settings
SECURITY_HIGH = 1
SECURITY_MEDIUM = 3  # '2' corresponds to deprecated TBB medium-high setting
SECURITY_LOW = 4


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


def read_file(file_path, mode='r'):
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
    if torrc is None:
        torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
                 'SOCKSPort': str(cm.STEM_SOCKS_PORT),
                 'DataDirectory': tempfile.mkdtemp()}

    return launch_tor_with_config(config=torrc, tor_cmd=tor_binary)


def set_tbb_pref(driver, name, value):
    try:
        script = 'const { Services } = '\
                 'ChromeUtils.import("resource://gre/modules/Services.jsm");'
        script += 'Services.prefs.'
        if isinstance(value, bool):
            script += 'setBoolPref'
        elif isinstance(value, (str)):
            script += 'setStringPref'
        else:
            script += 'setIntPref'
        script += '({0}, {1});'.format(json.dumps(name), json.dumps(value))
        driver.set_context(driver.CONTEXT_CHROME)
        driver.execute_script(script)
    except Exception:
        raise
    finally:
        driver.set_context(driver.CONTEXT_CONTENT)


def set_security_level(driver, level):
    if level not in {SECURITY_HIGH, SECURITY_MEDIUM, SECURITY_LOW}:
        raise ValueError("Invalid Tor Browser security setting: " + str(level))

    set_tbb_pref(driver, "extensions.torbutton.security_slider", level)
    sleep(1)  # wait for the pref to update


def disable_js(driver):
    set_tbb_pref(driver, "javascript.enabled", False)
    sleep(1)  # wait for the pref to update
