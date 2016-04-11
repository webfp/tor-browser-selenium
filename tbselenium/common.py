from os.path import join

# DEFAULT TBB PATHS: according to latest TBB version (5.5.4)
# Old TBB versions (V4.X or below) have a different directory structure
DEFAULT_TBB_BROWSER_DIR = 'Browser'
DEFAULT_TBB_FX_BINARY_PATH = join('Browser', 'firefox')
DEFAULT_TOR_BINARY_DIR = join('Browser', 'TorBrowser', 'Tor')
DEFAULT_TOR_BINARY_PATH = join(DEFAULT_TOR_BINARY_DIR, 'tor')
DEFAULT_TBB_DATA_DIR = join('Browser', 'TorBrowser', 'Data')
DEFAULT_TBB_PROFILE_PATH = join(DEFAULT_TBB_DATA_DIR, 'Browser',
                                'profile.default')
DEFAULT_TOR_DATA_PATH = join(DEFAULT_TBB_DATA_DIR, 'Tor')
DEFAULT_FONTCONFIG_PATH = join(DEFAULT_TBB_DATA_DIR, 'fontconfig')
FONTCONFIG_FILE = "fonts.conf"
DEFAULT_FONTS_CONF_PATH = join(DEFAULT_FONTCONFIG_PATH, FONTCONFIG_FILE)
DEFAULT_BUNDLED_FONTS_PATH = join('Browser', 'fonts')

# TOR PORTS
DEFAULT_SOCKS_PORT = 9050
DEFAULT_CONTROL_PORT = 9051

TBB_SOCKS_PORT = 9150
TBB_CONTROL_PORT = 9151

# TOR CONTROLLER
STREAM_CLOSE_TIMEOUT = 20  # wait 20 seconds before raising an alarm signal
# otherwise we had many cases where get_streams hanged

# Test constants
CHECK_TPO_URL = "http://check.torproject.org"
TEST_URL = CHECK_TPO_URL
ABOUT_TOR_URL = "about:tor"
# Default size for the virtual display
DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800
# virt_display is a string in the form of WxH
# W = width of the virtual display
# H = height of the virtual display
# e.g. "1280x800" or "800x600"
DEFAULT_XVFB_WINDOW_SIZE = "%sx%s" % (DEFAULT_XVFB_WIN_W, DEFAULT_XVFB_WIN_H)

# Which tor process/binary to use
LAUNCH_NEW_TBB_TOR = 0  # use tor in TBB, launch a new process
USE_SYSTEM_TOR = 1  # use the tor installed and running on the system


class TBDriverPathError(Exception):
    pass
