from os import environ
try:
    from pyvirtualdisplay import Display
except ImportError:  # we don't need/install it when running CI tests
    pass

# Default size for the virtual display
DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800

test_conf = {"xvfb_display": None}


def start_xvfb(win_width=DEFAULT_XVFB_WIN_W,
               win_height=DEFAULT_XVFB_WIN_H):
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    if xvfb_display:
        xvfb_display.stop()


def pytest_sessionstart(session):
    if "TRAVIS" not in environ and "NO_XVFB" not in environ:
        test_conf["xvfb_display"] = start_xvfb()


def pytest_sessionfinish(session, exitstatus):
    xvfb_display = test_conf["xvfb_display"]
    if xvfb_display:
        stop_xvfb(xvfb_display)
