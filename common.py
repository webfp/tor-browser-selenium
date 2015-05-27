import os
import platform


class TBBTarballVerificationError(Exception):
    pass


class TBBSigningKeyImportError(Exception):
    pass


class TBBGetRecommendedVersionError(Exception):
    pass


class DumpcapTimeoutError(Exception):
    pass


env_vars = os.environ
# whether we're running on Travis CI or not
running_in_CI = "CONTINUOUS_INTEGRATION" in env_vars and "TRAVIS" in env_vars

architecture = platform.architecture()
if '64' in architecture[0]:
    arch = '64'
    machine = 'x86_64'
elif '32' in architecture[0]:
    arch = '32'
    machine = 'i686'
else:
    raise RuntimeError('Architecture is not known: %s' % architecture)

# shortcuts
path = os.path
join = path.join
dirname = os.path.dirname
expanduser = os.path.expanduser

# timeouts and pauses
PAUSE_BETWEEN_SITES = 5      # pause before crawling a new site
WAIT_IN_SITE = 5             # time to wait after the page loads
PAUSE_BETWEEN_INSTANCES = 4  # pause before visiting the same site (instances)
SOFT_VISIT_TIMEOUT = 120     # timeout used by selenium and dumpcap
# signal based hard timeout in case soft timeout fails
HARD_VISIT_TIMEOUT = SOFT_VISIT_TIMEOUT + 10
# max dumpcap size in KB
MAX_DUMP_SIZE = 30000
# max filename length
MAX_FNAME_LENGTH = 200

DISABLE_RANDOMIZEDPIPELINENING = False  # use with caution!
STREAM_CLOSE_TIMEOUT = 20  # wait 20 seconds before raising an alarm signal
# otherwise we had many cases where get_streams hanged

XVFB_W = 1280
XVFB_H = 720

# Tor browser version suffixes
# The version used by Wang & Goldberg
TBB_V_2_4_7_A1 = "2.4.7-alpha-1"
TBB_WANG_AND_GOLDBERG = TBB_V_2_4_7_A1

TBB_V_3_5 = "3.5"
TBB_V_4_0_8 = "4.0.8"
TBB_DEFAULT_VERSION = TBB_V_4_0_8

TBB_KNOWN_VERSIONS = [TBB_V_2_4_7_A1, TBB_V_3_5, TBB_V_4_0_8]

# Default paths
BASE_DIR = path.abspath(os.path.dirname(__file__))
DATASET_DIR = join(BASE_DIR, "datasets")
ALEXA_DIR = join(DATASET_DIR, "alexa")
TEST_DIR = join(BASE_DIR, 'test')
TEST_FILES_DIR = join(TEST_DIR, 'files')
DUMMY_TEST_DIR = join(TEST_FILES_DIR, 'dummy')
DUMMY_TEST_DIR_TARGZIPPED = DUMMY_TEST_DIR + ".tar.gz"
TBB_TEST_TARBALL = join(TEST_FILES_DIR,
                        'tor-browser-linux64-4.0.99_en-US.tar.xz')
TBB_TEST_TARBALL_EXTRACTED = join(TEST_FILES_DIR,
                                  'tor-browser-linux64-4.0.99_en-US')
RESULTS_DIR = join(BASE_DIR, 'results')
ETC_DIR = join(BASE_DIR, 'etc')
PERMISSIONS_DB = join(ETC_DIR, 'permissions.sqlite')
HOME_PATH = expanduser('~')
TBB_BASE_DIR = join(BASE_DIR, 'tbb')

# Top URLs localized (DE) to prevent the effect of localization
LOCALIZED_DATASET = join(ETC_DIR, "localized-urls-100-top.csv")

# Experiment type determines what to do during the visits
EXP_TYPE_WANG_AND_GOLDBERG = "wang_and_goldberg"  # setting from WPES'13 paper
EXP_TYPE_MULTITAB_ALEXA = "multitab_alexa"  # open Alexa sites in multiple tabs

# Tor ports
SOCKS_PORT = 9050
CONTROLLER_PORT = 9051
MAX_ENTRY_GUARDS = "1"

# defaults for batch and instance numbers
NUM_BATCHES = 10
NUM_INSTANCES = 4
MAX_SITES_PER_TOR_PROCESS = 100  # reset tor process after crawling 100 sites

# torrc dictionaries
TORRC_DEFAULT = {'SocksPort': str(SOCKS_PORT),
                 'ControlPort': str(CONTROLLER_PORT)}

TORRC_WANG_AND_GOLDBERG = {'SocksPort': str(SOCKS_PORT),
                           'ControlPort': str(CONTROLLER_PORT),
                           'MaxCircuitDirtiness': '600000',
                           'UseEntryGuards': '0'
                           }

# Directory structure and paths depend on TBB versions
# Path to Firefox binary in TBB dir
TBB_V2_FF_BIN_PATH = join('App', 'Firefox', 'firefox')
TBB_V3_FF_BIN_PATH = join('Browser', 'firefox')
TBB_V4_FF_BIN_PATH = join('Browser', 'firefox')

TBB_FF_BIN_PATH_DICT = {"2": TBB_V2_FF_BIN_PATH,
                        "3": TBB_V3_FF_BIN_PATH,
                        "4": TBB_V4_FF_BIN_PATH,
                        }

# Path to Firefox profile in TBB dir
TBB_V2_PROFILE_PATH = join('Data', 'profile')
TBB_V3_PROFILE_PATH = join('Data', 'Browser', 'profile.default')
TBB_V4_PROFILE_PATH = join('Browser', 'TorBrowser', 'Data',
                           'Browser', 'profile.default')

TBB_PROFILE_DIR_DICT = {"2": TBB_V2_PROFILE_PATH,
                        "3": TBB_V3_PROFILE_PATH,
                        "4": TBB_V4_PROFILE_PATH,
                        }

# Path to Tor binary in TBB dir
TOR_V2_BINARY_PATH = join('App', 'tor')
TOR_V3_BINARY_PATH = join('Tor', 'tor')
TOR_V4_BINARY_PATH = join('Browser', 'TorBrowser', 'Tor', 'tor')

TOR_BINARY_PATH_DICT = {"2": TOR_V2_BINARY_PATH,
                        "3": TOR_V3_BINARY_PATH,
                        "4": TOR_V4_BINARY_PATH,
                        }
# Path to Tor binary in TBB dir
TOR_V2_DATA_DIR = join('Data', 'Tor')
TOR_V3_DATA_DIR = join('Data', 'Tor')
TOR_V4_DATA_DIR = join('Browser', 'TorBrowser', 'Data', 'Tor')

TOR_DATA_DIR_DICT = {"2": TOR_V2_DATA_DIR,
                     "3": TOR_V3_DATA_DIR,
                     "4": TOR_V4_DATA_DIR,
                     }


def get_tbb_major_version(version):
    """Return major version of TBB."""
    return version.split(".")[0]


def get_tbb_dirname(version, os_name="linux", lang="en-US"):
    """Return path for Tor Browser Bundle for given version and bits."""
    return "tor-browser-%s%s-%s_%s" % (os_name, arch, version, lang)


def get_tbb_path(version, os_name="linux", lang="en-US"):
    """Return path for Tor Browser Bundle for given version and bits."""
    dirname = get_tbb_dirname(version, os_name, lang)
    return join(TBB_BASE_DIR, dirname)


def get_tb_bin_path(version, os_name="linux", lang="en-US"):
    """Return a binary path for Tor Browser."""
    major = get_tbb_major_version(version)
    # bin_path = TBB_V3_FF_BIN_PATH if major is "3" else TBB_V2_FF_BIN_PATH
    bin_path = TBB_FF_BIN_PATH_DICT[major]
    dir_path = get_tbb_path(version, os_name, lang)
    return join(dir_path, bin_path)


def get_tor_bin_path(version, os_name="linux", lang="en-US"):
    """Return a binary path for Tor."""
    major = get_tbb_major_version(version)
    bin_path = TOR_BINARY_PATH_DICT[major]
    dir_path = get_tbb_path(version, os_name, lang)
    return join(dir_path, bin_path)


def get_tbb_profile_path(version, os_name="linux", lang="en-US"):
    """Return profile path for Tor Browser Bundle."""
    major = get_tbb_major_version(version)
    profile = TBB_PROFILE_DIR_DICT[major]
    dir_path = get_tbb_path(version, os_name, lang)
    return join(dir_path, profile)


def get_tor_data_path(version, os_name="linux", lang="en-US"):
    """Return the path for Data dir of Tor."""
    major = get_tbb_major_version(version)
    data_path = TOR_DATA_DIR_DICT[major]
    tbb_path = get_tbb_path(version, os_name, lang)
    return join(tbb_path, data_path)
