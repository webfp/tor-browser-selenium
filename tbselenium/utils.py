import tempfile
import tbselenium.common as cm
import json
from os import environ
from os.path import dirname, isfile, join
from time import sleep
from tbselenium.exceptions import StemLaunchError
from selenium.webdriver.common.utils import is_connectable
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException, NoSuchElementException


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
TB_SECURITY_LEVEL_STANDARD = 'standard'
TB_SECURITY_LEVEL_SAFER = 'safer'
TB_SECURITY_LEVEL_SAFEST = 'safest'

TB_SECURITY_LEVELS = [
    TB_SECURITY_LEVEL_STANDARD,
    TB_SECURITY_LEVEL_SAFER,
    TB_SECURITY_LEVEL_SAFEST
]


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
        # driver.set_context(driver.CONTEXT_CHROME)
        with driver.context(driver.CONTEXT_CHROME):
            driver.execute_script(script)
    except Exception:
        raise
    finally:
        driver.set_context(driver.CONTEXT_CONTENT)


def set_security_level(driver, level):
    if level not in TB_SECURITY_LEVELS:
        raise ValueError(f"Invalid Tor Browser security setting: {level}")
    open_security_level_panel(driver)
    click_to_set_security_level(driver, level)


# Based on https://gitlab.torproject.org/tpo/applications/tor-browser-bundle-testsuite/-/blob/main/marionette/tor_browser_tests/test_security_level_ui.py  # noqa
def open_security_level_panel(driver):
    with driver.context('chrome'):
        # emulate a click on the security level button
        driver.execute_script(
            'document.getElementById("security-level-button").click();')
        try:
            #  12.5a7 and later
            driver.execute_script(
                'document.getElementById("securityLevel-settings").click();')
        except JavascriptException:
            driver.find_element(By.ID,
                                'securityLevel-advancedSecuritySettings').click()
        # settings_button = driver.find_element(By.ID, "securityLevel-settings")
        # settings_button.click()


def click_to_set_security_level(driver, level):
    assert level in TB_SECURITY_LEVELS
    with driver.context('content'):
        # makes sure the security level panel is highlighted/scrolled to
        spotlight = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "spotlight"))
        )
        assert spotlight.get_attribute("data-subcategory") == "securitylevel"
        # click on the radio button for the desired security level
        try:
            # 12.5a7 and later
            level_idx = TB_SECURITY_LEVELS.index(level) + 1
            # CSS selector for the radio button, extracted via devtools
            driver.find_element(
                By.CSS_SELECTOR,
                f'vbox.securityLevel-radio-option:nth-child({level_idx}) >'
                ' radio:nth-child(1)').click()
        except NoSuchElementException:
            driver.find_element(
                'css selector', f'#securityLevel-vbox-{level} radio').click()


def disable_js(driver):
    set_tbb_pref(driver, "javascript.enabled", False)
    sleep(1)  # wait for the pref to update
