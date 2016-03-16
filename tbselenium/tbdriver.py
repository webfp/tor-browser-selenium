import shutil
import socket
import sqlite3
from httplib import CannotSendRequest
from os import environ
from os.path import isdir, isfile, join, dirname

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
from tld import get_tld

import common as cm
from utils import clone_dir_temporary


class TorBrowserDriver(Firefox):
    """
    Extend Firefox webdriver to automate Tor Browser.
    """
    canvas_exceptions = []

    def __init__(self,
                 tbb_path=None,
                 tbb_binary_path=None,
                 tbb_profile_path=None,
                 tbb_logfile_path=None,
                 pref_dict={},
                 socks_port=cm.DEFAULT_SOCKS_PORT,
                 # pass a string in the form of WxH to enable virtual display
                 # e.g. virt_display="1280x800" or virt_display="800x600"
                 virt_display="",  # empty string means XVFB is disabled.
                 pollute=True):

        # Check that either the TBB directory of the latest TBB version
        # or the path to the tor browser binary and profile are passed.
        assert (tbb_path or tbb_binary_path and tbb_profile_path)
        if tbb_path:
            tbb_path = tbb_path.rstrip('/')
            tbb_binary_path = join(tbb_path, cm.DEFAULT_TBB_BINARY_PATH)
            tbb_profile_path = join(tbb_path, cm.DEFAULT_TBB_PROFILE_PATH)

        # Make sure the paths exist
        assert (isfile(tbb_binary_path) and isdir(tbb_profile_path))
        self.tbb_binary_path = tbb_binary_path
        self.tbb_profile_path = tbb_profile_path
        self.temp_profile_path = None
        self.socks_port = socks_port
        self.pollute = pollute
        self.virt_display = virt_display
        if virt_display:
            win_w, win_h = (int(dim) for dim in virt_display.split("x"))
            self.start_xvfb(win_w, win_h)
        # Initialize Tor Browser's profile
        self.profile = self.init_tbb_profile()

        # Initialize Tor Browser's binary
        self.binary = self.get_tbb_binary(logfile=tbb_logfile_path)
        self.update_prefs(pref_dict)

        # Initialize capabilities
        self.capabilities = DesiredCapabilities.FIREFOX
        self.capabilities.update({'handlesAlerts': True,
                                  'databaseEnabled': True,
                                  'javascriptEnabled': True,
                                  'browserConnectionEnabled': True})

        try:
            super(TorBrowserDriver, self).__init__(firefox_profile=self.profile,
                                                   firefox_binary=self.binary,
                                                   capabilities=self.capabilities)
            self.is_running = True
        except WebDriverException as wd_exc:
            print("[tbselenium] WebDriverException while connecting to Webdriver: %s" % wd_exc)
        except socket.error as skt_err:
            print("[tbselenium] Socker error connecting to Webdriver: %s" % skt_err.message)
        except Exception as exc:
            print("[tbselenium] Error connecting to Webdriver: %s" % exc)

    def update_prefs(self, pref_dict):
        # Set homepage to a blank tab
        self.profile.set_preference('browser.startup.page', "0")
        self.profile.set_preference('browser.startup.homepage', 'about:newtab')

        # Configure Firefox to use Tor SOCKS proxy
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', self.socks_port)
        self.profile.set_preference('extensions.torlauncher.prompt_at_startup', 0)
        # http://www.w3.org/TR/webdriver/#page-load-strategies-1
        # wait for all frames to load and make sure there's no
        # outstanding http requests (except AJAX)
        # https://code.google.com/p/selenium/wiki/DesiredCapabilities
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        # Note that W3C doesn't mention "conservative", this may change in the
        # upcoming versions of the Firefox Webdriver
        # https://w3c.github.io/webdriver/webdriver-spec.html#the-page-load-strategy

        # Prevent Tor Browser running its own Tor process
        self.profile.set_preference('extensions.torlauncher.start_tor', False)
        self.profile.set_preference('extensions.torbutton.versioncheck_enabled', False)
        self.profile.set_preference('permissions.memory_only', False)
        for pref_name, pref_val in pref_dict.iteritems():
            self.profile.set_preference(pref_name, pref_val)
        self.profile.update_preferences()

    def export_lib_path(self):
        """Add the Tor Browser binary path to the library variable."""
        environ["LD_LIBRARY_PATH"] = dirname(self.tbb_binary_path)

    def get_tbb_binary(self, logfile=None):
        """Return FirefoxBinary pointing to the TBB's firefox binary."""
        tbb_logfile = None
        if logfile:
            tbb_logfile = open(logfile, 'a+')

        # In case you get an error for the unknown log_file, make sure your
        # Selenium version is compatible with the Firefox version in TBB.
        # Another common output in case of incompatibility is an error
        # for TorBrowserDriver not having a 'session_id' property.
        return FirefoxBinary(firefox_path=self.tbb_binary_path,
                             log_file=tbb_logfile)

    @classmethod
    def add_exception(cls, url):
        """Add top level domain of `url` to canvas_exceptions list."""
        cls.canvas_exceptions.append(get_tld(url))

    def add_canvas_permission(self, profile_path):
        """Create a permission db (permissions.sqlite) and add an
        exception for the canvas image extraction. Otherwise screenshots
        taken by Selenium will be just blank images due to the canvas
        fingerprinting defense in the Tor Browser.
        """
        connect_to_db = sqlite3.connect
        perm_db = connect_to_db(join(profile_path, "permissions.sqlite"))
        cursor = perm_db.cursor()
        # http://mxr.mozilla.org/mozilla-esr31/source/build/automation.py.in
        cursor.execute("PRAGMA user_version=3")
        cursor.execute("""CREATE TABLE IF NOT EXISTS moz_hosts (
          id INTEGER PRIMARY KEY,
          host TEXT,
          type TEXT,
          permission INTEGER,
          expireType INTEGER,
          expireTime INTEGER,
          appId INTEGER,
          isInBrowserElement INTEGER)""")
        for domain in self.canvas_exceptions:
            # print("Adding canvas/extractData permission for %s" % domain)
            qry = """INSERT INTO 'moz_hosts'
            VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % domain
            cursor.execute(qry)
        perm_db.commit()
        cursor.close()

    def init_tbb_profile(self):
        """Create a Firefox profile pointing to a profile dir path."""
        profile_path = self.tbb_profile_path
        if not self.pollute:
            self.temp_profile_path = clone_dir_temporary(self.tbb_profile_path)
            profile_path = self.temp_profile_path
        self.add_canvas_permission(profile_path)
        try:
            tbb_profile = webdriver.FirefoxProfile(profile_path)
        except Exception as exc:
            print("[tbselenium] Error creating the TB profile %s" % exc)
        return tbb_profile

    def quit(self):
        """Overrides the base class method. Quits driver and closes virtual display ."""
        self.is_running = False
        try:
            super(TorBrowserDriver, self).quit()
        except CannotSendRequest as exc:
            print("[tbselenium] CannotSendRequest while quitting TorBrowserDriver %s" % exc)
            # following is copied from webdriver.firefox.webdriver.quit() which
            # was interrupted due to an unhandled CannotSendRequest exception.
            self.binary.kill()  # kill the browser
            try:
                shutil.rmtree(self.profile.path)
                if self.profile.tempfolder is not None:
                    shutil.rmtree(self.profile.tempfolder)
            except Exception as e:
                print("[tbselenium] " + str(e))
        except Exception as exc:
            print("[tbselenium] Exception while quitting TorBrowserDriver %s" % exc)
        finally:
            # remove profile dir
            if self.temp_profile_path is not None:
                shutil.rmtree(self.temp_profile_path)
            # remove virtual display
            if self.xvfb_display:
                self.xvfb_display.stop()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.quit()
