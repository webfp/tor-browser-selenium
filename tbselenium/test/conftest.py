from os import environ
import tempfile
from os.path import join, dirname
from tbselenium import common as cm
from tbselenium.test import TBB_PATH
try:
    from stem.process import launch_tor_with_config
except ImportError:
    pass

try:
    from pyvirtualdisplay import Display
except ImportError:  # we don't need/install it when running CI tests
    pass

# Default size for the virtual display
DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800

test_conf = {}


def start_xvfb(win_width=DEFAULT_XVFB_WIN_W,
               win_height=DEFAULT_XVFB_WIN_H):
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    if xvfb_display:
        xvfb_display.stop()


def start_tor_with_default_ports():
    custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
    environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)
    temp_data_dir = tempfile.mkdtemp()
    torrc = {'ControlPort': str(cm.DEFAULT_CONTROL_PORT),
             'SOCKSPort': str(cm.DEFAULT_SOCKS_PORT),
             'DataDirectory': temp_data_dir}
    return launch_tor_with_config(config=torrc, tor_cmd=custom_tor_binary)


def pytest_sessionstart(session):
    if "TRAVIS" not in environ and "NO_XVFB" not in environ:
        test_conf["xvfb_display"] = start_xvfb()
    if "TRAVIS" in environ:
        test_conf["tor_process"] = start_tor_with_default_ports()


def pytest_sessionfinish(session, exitstatus):
    xvfb_display = test_conf.get("xvfb_display")
    tor_process = test_conf.get("tor_process")
    if xvfb_display:
        stop_xvfb(xvfb_display)

    if tor_process:
        tor_process.kill()
