from os.path import join


# DEFAULT TBB PATHS: according to latest TBB version (5.3)
DEFAULT_TBB_BINARY_PATH = join('Browser', 'firefox')
DEFAULT_TBB_PROFILE_PATH = join('Browser', 'TorBrowser', 'Data', 'Browser', 'profile.default')
DEFAULT_TOR_BINARY_PATH = join('Browser', 'TorBrowser', 'Tor', 'tor')
DEFAULT_TOR_DATA_PATH = join('Browser', 'TorBrowser', 'Data', 'Tor')

# TOR PORTS
SOCKS_PORT = 9050
CONTROLLER_PORT = 9051

# TOR CONTROLLER
STREAM_CLOSE_TIMEOUT = 20  # wait 20 seconds before raising an alarm signal
# otherwise we had many cases where get_streams hanged
TEST_URL = "http://check.torproject.org"