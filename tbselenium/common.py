from os.path import join


# DEFAULT TBB PATHS: according to latest TBB version (5.3)
DEFAULT_TBB_BINARY_PATH = join('Browser', 'firefox')
DEFAULT_TBB_PROFILE_PATH = join('Browser', 'TorBrowser', 'Data', 'Browser', 'profile.default')
DEFAULT_TOR_BINARY_PATH = join('Browser', 'TorBrowser', 'Tor', 'tor')

# TOR PORTS
SOCKS_PORT = 9050
CONTROLLER_PORT = 9051
