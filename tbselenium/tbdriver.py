import shutil
from os import environ, chdir
from os.path import isdir, isfile, join, abspath
from time import sleep
from distutils.version import LooseVersion
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.common.utils import is_connectable
import tbselenium.common as cm
from tbselenium.utils import add_canvas_permission
from tbselenium.tbbinary import TBBinary
from tbselenium.exceptions import (TBDriverConfigError, TBDriverPortError,
                                   TBDriverPathError)


try:
    from httplib import CannotSendRequest
except ImportError:
    from http.client import CannotSendRequest


class TorBrowserDriver(FirefoxDriver):
    """
    Extend Firefox webdriver to automate Tor Browser.
    """
    def __init__(self,
                 tbb_path="",
                 tor_cfg=cm.LAUNCH_NEW_TBB_TOR,
                 tbb_fx_binary_path="",
                 tbb_profile_path="",
                 tbb_logfile_path="",
                 tor_data_dir="",
                 pref_dict={},
                 socks_port=None,
                 canvas_allowed_hosts=[],
                 timeout=cm.TB_INIT_TIMEOUT):

        self.tor_cfg = tor_cfg
        self.setup_tbb_paths(tbb_path, tbb_fx_binary_path,
                             tbb_profile_path, tor_data_dir)
        self.canvas_allowed_hosts = canvas_allowed_hosts
        self.profile = webdriver.FirefoxProfile(self.tbb_profile_path)
        add_canvas_permission(self.profile.path, self.canvas_allowed_hosts)
        self.init_socks_port(tor_cfg, socks_port)
        self.init_prefs(pref_dict)
        self.init_tb_version()
        self.setup_capabilities()
        self.export_env_vars()
        self.binary = self.get_tb_binary(logfile=tbb_logfile_path)
        super(TorBrowserDriver, self).__init__(firefox_profile=self.profile,
                                               firefox_binary=self.binary,
                                               capabilities=self.capabilities,
                                               timeout=timeout)
        self.is_running = True
        sleep(1)

    def init_socks_port(self, tor_cfg, socks_port):
        """Check SOCKS port and Tor config inputs."""
        if tor_cfg not in [cm.USE_RUNNING_TOR, cm.LAUNCH_NEW_TBB_TOR]:
            raise TBDriverConfigError("Unrecognized Tor config (tor_cfg)")

        if socks_port is None:
            if tor_cfg == cm.USE_RUNNING_TOR:
                socks_port = cm.DEFAULT_SOCKS_PORT  # 9050
            else:
                socks_port = cm.TBB_SOCKS_PORT  # 9150

        if tor_cfg == cm.LAUNCH_NEW_TBB_TOR:
            if is_connectable(socks_port):
                raise TBDriverPortError("SOCKS port %s is already in use"
                                        % socks_port)
            if socks_port != cm.TBB_SOCKS_PORT:
                # No support for launching TBB's Tor on a custom port, use Stem
                raise TBDriverPortError("Can only launch Tor on TBB's default"
                                        "port (9150). Use Stem for launching"
                                        "Tor on a custom SOCKS port")
        elif tor_cfg == cm.USE_RUNNING_TOR:
            if not is_connectable(socks_port):
                raise TBDriverPortError("SOCKS port %s is not listening"
                                        % socks_port)
        self.socks_port = socks_port

    def setup_tbb_paths(self, tbb_path, tbb_fx_binary_path, tbb_profile_path,
                        tor_data_dir):
        """Update instance variables based on the passed paths.

        TorBrowserDriver can be initialized by passing either
        1) path to TBB directory, or
        2) path to TBB's Firefox binary and profile
        """
        if not (tbb_path or (tbb_fx_binary_path and tbb_profile_path)):
            raise TBDriverPathError("Either TBB path or Firefox profile"
                                    " and binary path should be provided"
                                    " %s" % tbb_path)

        if tbb_path:
            if not isdir(tbb_path):
                raise TBDriverPathError("TBB path is not a directory %s"
                                        % tbb_path)
            tbb_fx_binary_path = join(tbb_path, cm.DEFAULT_TBB_FX_BINARY_PATH)
            tbb_profile_path = join(tbb_path, cm.DEFAULT_TBB_PROFILE_PATH)
        if not isfile(tbb_fx_binary_path):
            raise TBDriverPathError("Invalid Firefox binary %s"
                                    % tbb_fx_binary_path)
        if not isdir(tbb_profile_path):
            raise TBDriverPathError("Invalid Firefox profile dir %s"
                                    % tbb_profile_path)
        self.tbb_path = abspath(tbb_path)
        self.tbb_profile_path = abspath(tbb_profile_path)
        self.tbb_fx_binary_path = abspath(tbb_fx_binary_path)
        self.tbb_browser_dir = join(tbb_path, cm.DEFAULT_TBB_BROWSER_DIR)
        if tor_data_dir:
            self.tor_data_dir = tor_data_dir  # only relevant if we launch tor
        else:
            self.tor_data_dir = join(tbb_path, cm.DEFAULT_TOR_DATA_PATH)
        # TB can't find bundled "fonts" if we don't switch to tbb_browser_dir
        chdir(self.tbb_browser_dir)

    def load_url(self, url, wait_on_page=0, wait_for_page_body=False):
        """Load a URL and wait before returning.

        If you query/manipulate DOM or execute a script immediately
        after the page load, you may get the following error:

            "WebDriverException: Message: waiting for doc.body failed"

        To prevent this, set wait_for_page_body to True, and driver
        will wait for the page body to become available before it returns.

        """
        self.get(url)
        if wait_for_page_body:
            # if the page can't be loaded this will raise a TimeoutException
            self.find_element_by("body", find_by=By.TAG_NAME)
        sleep(wait_on_page)

    def find_element_by(self, selector, timeout=30,
                        find_by=By.CSS_SELECTOR):
        """Wait until the element matching the selector appears or timeout."""
        return WebDriverWait(self, timeout).until(
            EC.presence_of_element_located((find_by, selector)))

    def add_ports_to_fx_banned_ports(self, socks_port, control_port):
        """By default, ports 9050,9051,9150,9151 are banned in TB.

        If we use a tor process running on a custom SOCKS port, we add SOCKS
        and control ports to the following prefs:
            network.security.ports.banned
            extensions.torbutton.banned_ports
        """
        if socks_port in cm.KNOWN_SOCKS_PORTS:
            return
        tb_prefs = self.profile.default_preferences
        set_pref = self.profile.set_preference
        DEFAULT_BANNED_PORTS = "9050,9051,9150,9151"
        for port_ban_pref in cm.PORT_BAN_PREFS:
            banned_ports = tb_prefs.get(port_ban_pref, DEFAULT_BANNED_PORTS)
            set_pref(port_ban_pref, "%s,%s,%s" %
                     (banned_ports, socks_port, control_port))

    def set_tb_prefs_for_using_system_tor(self, control_port):
        """Set the preferences suggested by start-tor-browser script
        to run TB with system-installed Tor.

        We set these prefs for running with Tor started with Stem as well.
        """
        set_pref = self.profile.set_preference
        # Prevent Tor Browser running its own Tor process
        set_pref('extensions.torlauncher.start_tor', False)
        # TODO: investigate why we're asked to disable 'block_disk'
        set_pref('extensions.torbutton.block_disk', False)
        set_pref('extensions.torbutton.custom.socks_host', '127.0.0.1')
        set_pref('extensions.torbutton.custom.socks_port', self.socks_port)
        set_pref('extensions.torbutton.inserted_button', True)
        set_pref('extensions.torbutton.launch_warning', False)
        set_pref('extensions.torbutton.loglevel', 2)
        set_pref('extensions.torbutton.logmethod', 0)
        set_pref('extensions.torbutton.settings_method', 'custom')
        set_pref('extensions.torbutton.use_privoxy', False)
        set_pref('extensions.torlauncher.control_port', control_port)
        set_pref('extensions.torlauncher.loglevel', 2)
        set_pref('extensions.torlauncher.logmethod', 0)
        set_pref('extensions.torlauncher.prompt_at_startup', False)

    def init_prefs(self, pref_dict):
        control_port = self.socks_port + 1
        self.add_ports_to_fx_banned_ports(self.socks_port, control_port)
        set_pref = self.profile.set_preference
        set_pref('browser.startup.page', "0")
        set_pref('browser.startup.homepage', 'about:newtab')
        set_pref('extensions.torlauncher.prompt_at_startup', 0)
        # load strategy normal is equivalent to "onload"
        set_pref('webdriver.load.strategy', 'normal')
        # disable auto-update
        set_pref('app.update.enabled', False)
        set_pref('extensions.torbutton.versioncheck_enabled', False)
        # following is only needed for TBB < 4.5a3 to add canvas permissions
        set_pref('permissions.memory_only', False)
        set_pref('extensions.torbutton.prompted_language', True)
        # Configure Firefox to use Tor SOCKS proxy
        set_pref('network.proxy.socks_port', self.socks_port)
        set_pref('extensions.torbutton.socks_port', self.socks_port)
        # If your control port != socks_port+1, use pref_dict to overwrite
        set_pref('extensions.torlauncher.control_port', control_port)
        if self.tor_cfg == cm.LAUNCH_NEW_TBB_TOR:
            set_pref('extensions.torlauncher.start_tor', True)
            set_pref('extensions.torlauncher.tordatadir_path',
                     self.tor_data_dir)
        else:
            self.set_tb_prefs_for_using_system_tor(control_port)
        # pref_dict overwrites above preferences
        for pref_name, pref_val in pref_dict.items():
            set_pref(pref_name, pref_val)
        self.profile.update_preferences()

    def export_env_vars(self):
        """Setup LD_LIBRARY_PATH and HOME environment variables.

        We follow start-tor-browser script.
        """
        tor_binary_dir = join(self.tbb_path, cm.DEFAULT_TOR_BINARY_DIR)
        environ["LD_LIBRARY_PATH"] = tor_binary_dir
        environ["FONTCONFIG_PATH"] = join(self.tbb_path,
                                          cm.DEFAULT_FONTCONFIG_PATH)
        environ["FONTCONFIG_FILE"] = cm.FONTCONFIG_FILE
        environ["HOME"] = self.tbb_browser_dir
        # Add "TBB_DIR/Browser" to the PATH, see issue #10.
        current_path = environ["PATH"]
        environ["PATH"] = "%s:%s" % (self.tbb_browser_dir, current_path)

    def setup_capabilities(self):
        """Setup the required webdriver capabilities."""
        self.capabilities = DesiredCapabilities.FIREFOX
        self.capabilities.update({'handlesAlerts': True,
                                  'databaseEnabled': True,
                                  'javascriptEnabled': True,
                                  'browserConnectionEnabled': True})

    def get_tb_binary(self, logfile=None):
        """Return FirefoxBinary pointing to the TBB's firefox binary."""
        tbb_logfile = open(logfile, 'a+') if logfile else None
        return TBBinary(firefox_path=self.tbb_fx_binary_path,
                        log_file=tbb_logfile)

    @property
    def is_connection_error_page(self):
        """Check if we get a connection error, i.e. 'Problem loading page'."""
        return "ENTITY connectionFailure.title" in self.page_source

    def init_tb_version(self):
        self.tb_version = "Unknown"
        version_file = join(self.tbb_path, cm.TB_VERSIONS_PATH)
        for line in open(version_file):
            if "TORBROWSER_VERSION=" in line:
                self.tb_version = line.split("=")[-1]

    @property
    def supports_sec_slider(self):
        """Checks if security slider is supported or not."""
        version = self.tb_version
        if not version or (LooseVersion(version) < LooseVersion('4.5')):
            return False
        return True

    @property
    def supports_bundled_fonts(self):
        """Checks if shipped with bundled fonts or not."""
        version = self.tb_version
        # This comparison may fail for alpha versions, e.g. 4.5a1
        if not version or (LooseVersion(version) < LooseVersion('4.5')):
            return False
        return True

    def clean_up_profile_dirs(self):
        """Remove temporary profile directories.
        Only called when WebDriver.quit() is interrupted
        """
        tempfolder = self.profile.tempfolder
        profile_path = self.profile.path

        if tempfolder and isdir(tempfolder):
            shutil.rmtree(tempfolder)
        if isdir(profile_path):
            shutil.rmtree(profile_path)

    def quit(self):
        """Quit the driver. Clean up if the parent's quit fails."""
        self.is_running = False
        try:
            super(TorBrowserDriver, self).quit()
        except (CannotSendRequest, AttributeError) as exc:
            print("[tbselenium] %s" % exc)
            try:  # Clean up  if webdriver.quit() throws
                self.binary.kill()
                self.clean_up_profile_dirs()
            except Exception as e:
                print("[tbselenium] %s" % e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.quit()
