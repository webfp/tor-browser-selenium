import os
import shutil
import socket
import sqlite3
from httplib import CannotSendRequest
from os.path import isdir, isfile, join

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox

import common as cm
from utils import clone_dir_with_timestap


class TorBrowserDriver(Firefox):
    """
    Extends Selenium's Firefox driver to implement a Selenium driver for the Tor Browser.
    """
    exceptions = []

    def __init__(self,
                 tbb_path=None,
                 tbb_binary_path=None,
                 tbb_profile_path=None,
                 tbb_logfile_path=None,
                 pref_dict={}):

        # Check that either the TBB directory of the latest TBB version
        # or the path to the binary and profile are passed.
        assert (tbb_path or tbb_binary_path and tbb_profile_path)
        if tbb_path:
            tbb_binary_path = join(tbb_path, cm.DEFAULT_TBB_BINARY_PATH)
            tbb_profile_path = join(tbb_path, cm.DEFAULT_TBB_PROFILE_PATH)

        # Make sure the paths exist
        assert (isfile(tbb_binary_path) and isdir(tbb_profile_path))

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
        except WebDriverException as exc:
            print("WebDriverException while connecting to Webdriver: %s" % exc)
        except socket.error as skterr:
            print("Socker error connecting to Webdriver: %s" % skterr.message)
        except Exception as e:
            print("Error connecting to Webdriver: %s" % e)

    def update_prefs(self, pref_dict):
        # TODO check if the default prefs make sense
        # set homepage to a blank tab
        self.profile.set_preference('browser.startup.page', "0")
        self.profile.set_preference('browser.startup.homepage', 'about:newtab')

        # configure Firefox to use Tor SOCKS proxy
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', cm.SOCKS_PORT)
        self.profile.set_preference('extensions.torlauncher.prompt_at_startup', 0)
        # http://www.w3.org/TR/webdriver/#page-load-strategies-1
        # wait for all frames to load and make sure there's no
        # outstanding http requests (except AJAX)
        # https://code.google.com/p/selenium/wiki/DesiredCapabilities
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        # Note that W3C doesn't mention "conservative", this may change in the
        # upcoming versions of the Firefox Webdriver
        # https://w3c.github.io/webdriver/webdriver-spec.html#the-page-load-strategy

        # prevent Tor Browser running its own Tor process
        self.profile.set_preference('extensions.torlauncher.start_tor', False)
        self.profile.set_preference('extensions.torbutton.versioncheck_enabled', False)
        self.profile.set_preference('permissions.memory_only', False)
        for pref_name, pref_val in pref_dict.iteritems():
            self.profile.set_preference(pref_name, pref_val)
        self.profile.update_preferences()

    def export_lib_path(self):
        """Add the Tor Browser binary to the library path."""
        os.environ["LD_LIBRARY_PATH"] = os.path.dirname(self.tbb_binary_path)

    def get_tbb_binary(self, logfile=None):
        """Return FirefoxBinary pointing to the TBB's firefox binary."""
        tbb_logfile = None
        if logfile:
            tbb_logfile = open(logfile, 'a+')

        # in case you get an error for the unknown log_file, make sure your
        # Selenium version is compatible with the Firefox version in TBB.
        tbb_binary = FirefoxBinary(firefox_path=self.tbb_binary_path,
                                   log_file=tbb_logfile)
        return tbb_binary

    def add_canvas_permission(self):
        """Create a permission db (permissions.sqlite) and add an
        exception for the canvas image extraction. Otherwise screenshots
        taken by Selenium will be just blank images due to the canvas
        fingerprinting defense in the Tor Browser.
        """
        connect_to_db = sqlite3.connect
        perm_db = connect_to_db(join(self.temp_profile_path, "permissions.sqlite"))
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
        for domain in self.exceptions:
            print("Adding canvas/extractData permission for %s" % domain)
            qry = """INSERT INTO 'moz_hosts'
            VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % domain
            cursor.execute(qry)
        perm_db.commit()
        cursor.close()

    def init_tbb_profile(self):
        """Make a copy of profile dir and create a Firefox profile pointing to it."""
        self.temp_profile_path = clone_dir_with_timestap(self.tbb_profile_path)
        self.add_canvas_permission()
        try:
            tbb_profile = webdriver.FirefoxProfile(self.temp_profile_path)
        except Exception as exc:
            print("Error creating the TB profile %s" % exc)
        return tbb_profile

    def quit(self):
        """Overrides the base class method cleaning the timestamped profile."""
        self.is_running = False
        try:
            print("Quit: Removing profile dir")
            if self.temp_profile_path is not None:
                shutil.rmtree(self.temp_profile_path)
            super(TorBrowserDriver, self).quit()
        except CannotSendRequest as exc:
            print("CannotSendRequest while quitting TorBrowserDriver %s" % exc)
            # following is copied from webdriver.firefox.webdriver.quit() which
            # was interrupted due to an unhandled CannotSendRequest exception.
            self.binary.kill()  # kill the browser
            try:
                shutil.rmtree(self.profile.path)
                if self.profile.tempfolder is not None:
                    shutil.rmtree(self.profile.tempfolder)
            except Exception as e:
                print(str(e))
        except Exception as exc:
            print("Exception while quitting TorBrowserDriver %s" % exc)
