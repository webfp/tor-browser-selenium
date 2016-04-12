import pytest
from pyvirtualdisplay import Display
from os import environ
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


@pytest.fixture(scope="session", autouse=True)
def prepare_test_setup(request):
    """Run an XVFB display during the tests.
    Don't run on CI or if there's an env var named NO_XVFB
    """
    xvfb_display = None
    if "TRAVIS" not in environ and "NO_XVFB" not in environ:
        xvfb_display = start_xvfb()

    def teardown_test_setup():
        if xvfb_display:
            stop_xvfb(xvfb_display)

    request.addfinalizer(teardown_test_setup)
