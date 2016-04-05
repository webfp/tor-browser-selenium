from os.path import join

# DEFAULT TBB PATHS: according to latest TBB version (5.3)
DEFAULT_TBB_BROWSER_DIR = 'Browser'
DEFAULT_TBB_FX_BINARY_PATH = join('Browser', 'firefox')
DEFAULT_TBB_PROFILE_PATH = join('Browser', 'TorBrowser', 'Data', 'Browser',
                                'profile.default')
DEFAULT_TOR_BINARY_PATH = join('Browser', 'TorBrowser', 'Tor', 'tor')
DEFAULT_TOR_BINARY_DIR = join('Browser', 'TorBrowser', 'Tor')
DEFAULT_TOR_DATA_PATH = join('Browser', 'TorBrowser', 'Data', 'Tor')

# TOR PORTS
DEFAULT_SOCKS_PORT = 9050
REFACTOR_CONTROL_PORT = 9051

# TOR CONTROLLER
STREAM_CLOSE_TIMEOUT = 20  # wait 20 seconds before raising an alarm signal
# otherwise we had many cases where get_streams hanged

# Test constants
CHECK_TPO_URL = "http://check.torproject.org"
TEST_URL = CHECK_TPO_URL

# Default size for the virtual display
DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800
# virt_display is a string in the form of WxH
# W = width of the virtual display
# H = height of the virtual display
# e.g. "1280x800" or "800x600"
DEFAULT_XVFB_WINDOW_SIZE = "%sx%s" % (DEFAULT_XVFB_WIN_W, DEFAULT_XVFB_WIN_H)


class TBDriverPathError(Exception):
    pass
