from os import environ
import tempfile
from tbselenium.utils import start_xvfb, stop_xvfb, is_busy
from tbselenium.test.fixtures import launch_tbb_tor_with_stem_fixture
import tbselenium.common as cm
from tbselenium.test import TBB_PATH
from shutil import rmtree

test_conf = {}


def launch_tor():
    tor_process = None
    temp_data_dir = tempfile.mkdtemp()
    torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
             'SOCKSPort': str(cm.STEM_SOCKS_PORT),
             'DataDirectory': temp_data_dir}
    if not is_busy(cm.STEM_SOCKS_PORT):
        tor_process = launch_tbb_tor_with_stem_fixture(tbb_path=TBB_PATH,
                                                       torrc=torrc)
    return (temp_data_dir, tor_process)


def pytest_sessionstart(session):
    if ("TRAVIS" not in environ and
            ("NO_XVFB" not in environ or environ["NO_XVFB"] != "1")):
        test_conf["xvfb_display"] = start_xvfb()
    test_conf["temp_data_dir"], test_conf["tor_process"] = launch_tor()


def pytest_sessionfinish(session, exitstatus):
    xvfb_display = test_conf.get("xvfb_display")
    tor_process = test_conf.get("tor_process")
    if xvfb_display:
        stop_xvfb(xvfb_display)

    if tor_process:
        tor_process.kill()
    rmtree(test_conf["temp_data_dir"], ignore_errors=True)
