from os.path import join
from os import environ

# DEFAULT TBB PATHS works for TBB versions v4.x and above
# Old TBB versions (V3.X or below) have different directory structures
DEFAULT_TBB_BROWSER_DIR = 'Browser'
DEFAULT_TBB_TORBROWSER_DIR = join('Browser', 'TorBrowser')
DEFAULT_TBB_FX_BINARY_PATH = join('Browser', 'firefox')
DEFAULT_TOR_BINARY_DIR = join(DEFAULT_TBB_TORBROWSER_DIR, 'Tor')
DEFAULT_TOR_BINARY_PATH = join(DEFAULT_TOR_BINARY_DIR, 'tor')
DEFAULT_TBB_DATA_DIR = join(DEFAULT_TBB_TORBROWSER_DIR, 'Data')
DEFAULT_TBB_PROFILE_PATH = join(DEFAULT_TBB_DATA_DIR, 'Browser',
                                'profile.default')
DEFAULT_TOR_DATA_PATH = join(DEFAULT_TBB_DATA_DIR, 'Tor')
TB_CHANGE_LOG_PATH = join(DEFAULT_TBB_TORBROWSER_DIR,
                          'Docs', 'ChangeLog.txt')

# Directories for bundled fonts - Linux only
DEFAULT_FONTCONFIG_PATH = join(DEFAULT_TBB_DATA_DIR, 'fontconfig')
FONTCONFIG_FILE = "fonts.conf"
DEFAULT_FONTS_CONF_PATH = join(DEFAULT_FONTCONFIG_PATH, FONTCONFIG_FILE)
DEFAULT_BUNDLED_FONTS_PATH = join('Browser', 'fonts')

# SYSTEM TOR PORTS
DEFAULT_SOCKS_PORT = 9050
DEFAULT_CONTROL_PORT = 9051

# TBB TOR PORTS
TBB_SOCKS_PORT = 9150
TBB_CONTROL_PORT = 9151

# pick 9250, 9251 to avoid conflict
STEM_SOCKS_PORT = 9250
STEM_CONTROL_PORT = 9251

KNOWN_SOCKS_PORTS = [DEFAULT_SOCKS_PORT, TBB_SOCKS_PORT]
PORT_BAN_PREFS = ["extensions.torbutton.banned_ports",
                  "network.security.ports.banned"]

TB_INIT_TIMEOUT = 60

# Test constants
CHECK_TPO_URL = "http://check.torproject.org"
CHECK_TPO_HOST = "check.torproject.org"
TEST_URL = CHECK_TPO_URL
ABOUT_TOR_URL = "about:tor"

# Which tor process/binary to use
LAUNCH_NEW_TBB_TOR = 0  # use tor in TBB, launch a new process
USE_RUNNING_TOR = 1  # use the tor installed and running on the system

TRAVIS = "CI" in environ and "TRAVIS" in environ
