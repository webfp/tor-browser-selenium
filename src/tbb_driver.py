import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import firefox
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import shutil
import socket
import sqlite3
from httplib import CannotSendRequest
from tld import get_tld
import common as cm
from utils import clone_dir_with_timestap


class TorBrowserDriver(webdriver.Firefox, firefox.webdriver.RemoteWebDriver):
    def __init__(self, tbb_binary_path=None, tbb_profile_dir=None,
                 tbb_logfile_path=None,
                 tbb_version=cm.TBB_DEFAULT_VERSION, page_url="",
                 capture_screen=True, pref_dict=None):
        self.is_running = False
        self.tbb_version = tbb_version
        self.export_lib_path()
        # Initialize Tor Browser's profile
        self.page_url = page_url
        self.capture_screen = capture_screen
        self.profile = self.init_tbb_profile(tbb_version)
        # Initialize Tor Browser's binary
        self.binary = self.get_tbb_binary(tbb_version=self.tbb_version,
                                          logfile=tbb_logfile_path)

        self.update_prefs(pref_dict)
        # Initialize capabilities
        self.capabilities = DesiredCapabilities.FIREFOX
        self.capabilities.update({'handlesAlerts': True,
                                  'databaseEnabled': True,
                                  'javascriptEnabled': True,
                                  'browserConnectionEnabled': True})

        try:
            super(TorBrowserDriver, self)\
                .__init__(firefox_profile=self.profile,
                          firefox_binary=self.binary,
                          capabilities=self.capabilities)
            self.is_running = True
        except WebDriverException as exc:
            print("WebDriverException while connecting to Webdriver %s" % exc)
        except socket.error as skterr:
            print("Socker error connecting to Webdriver %s" % skterr.message)
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
        self.profile.set_preference(
            'extensions.torlauncher.prompt_at_startup',
            0)
        # http://www.w3.org/TR/webdriver/#page-load-strategies-1
        # wait for all frames to load and make sure there's no
        # outstanding http requests (except AJAX)
        # https://code.google.com/p/selenium/wiki/DesiredCapabilities
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        # Note that W3C doesn't mention "conservative", this may change in the
        # upcoming versions of the Firefox Webdriver
        # https://w3c.github.io/webdriver/webdriver-spec.html#the-page-load-strategy

        # prevent Tor Browser running it's own Tor process
        self.profile.set_preference('extensions.torlauncher.start_tor', False)
        self.profile.set_preference(
            'extensions.torbutton.versioncheck_enabled', False)
        self.profile.set_preference('permissions.memory_only', False)
        for pref_name, pref_val in pref_dict.iteritems():
            self.profile.set_preference(pref_name, pref_val)
        self.profile.update_preferences()

    def export_lib_path(self):
        os.environ["LD_LIBRARY_PATH"] = os.path.dirname(
            cm.get_tor_bin_path(self.tbb_version))

    def get_tbb_binary(self, tbb_version, binary=None, logfile=None):
        """Return FirefoxBinary pointing to the TBB's firefox binary."""
        tbb_logfile = None
        if not binary:
            binary = cm.get_tb_bin_path(tbb_version)
        if logfile:
            tbb_logfile = open(logfile, 'a+')

        # in case you get an error for the unknown log_file, make sure your
        # Selenium version is compatible with the Firefox version in TBB.
        tbb_binary = FirefoxBinary(firefox_path=binary,
                                   log_file=tbb_logfile)
        return tbb_binary

    def add_canvas_permission(self):
        """Create a permission db (permissions.sqlite) and add

        exception for the canvas image extraction. Otherwise screenshots
        taken by Selenium will be just blank images due to canvas
        fingerprinting defense in TBB."""

        connect_to_db = sqlite3.connect  # @UndefinedVariable
        perm_db = connect_to_db(os.path.join(self.prof_dir_path,
                                             "permissions.sqlite"))
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

        domain = get_tld(self.page_url)
        print("Adding canvas/extractData permission for %s" % domain)
        qry = """INSERT INTO 'moz_hosts'
        VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % domain
        cursor.execute(qry)
        perm_db.commit()
        cursor.close()

    def init_tbb_profile(self, version):
        profile_directory = cm.get_tbb_profile_path(version)
        self.prof_dir_path = clone_dir_with_timestap(profile_directory)
        if self.capture_screen and self.page_url:
            self.add_canvas_permission()
        try:
            tbb_profile = webdriver.FirefoxProfile(self.prof_dir_path)
        except Exception as exc:
            print("Error creating the TB profile %s" % exc)
        else:
            return tbb_profile

    def quit(self):
        """
        Overrides the base class method cleaning the timestamped profile.

        """
        self.is_running = False
        try:
            print("Quit: Removing profile dir")
            shutil.rmtree(self.prof_dir_path)
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
