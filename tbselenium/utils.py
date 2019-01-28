import tempfile
import tbselenium.common as cm
from os import environ
from os.path import dirname, isfile, join
from tbselenium.exceptions import StemLaunchError
from selenium.webdriver.common.utils import is_connectable
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep

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
    if torrc is None:
        torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
                 'SOCKSPort': str(cm.STEM_SOCKS_PORT),
                 'DataDirectory': tempfile.mkdtemp()}

    return launch_tor_with_config(config=torrc, tor_cmd=tor_binary)


def disable_js(driver):
    driver.get("about:config")
    accept_risk_button = driver.find_element_by_id("warningButton")
    if accept_risk_button:  # I accept the risk
        accept_risk_button.click()
    ActionChains(driver).send_keys(Keys.RETURN).\
        send_keys("javascript.enabled").perform()
    sleep(1)  # wait for the table update
    ActionChains(driver).send_keys(Keys.TAB).send_keys(Keys.RETURN).perform()
    sleep(1)  # wait for the pref to update
