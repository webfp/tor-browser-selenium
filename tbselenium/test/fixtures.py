from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.exceptions import StemLaunchError, TorBrowserDriverInitError
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.utils import is_connectable

try:
    from httplib import CannotSendRequest
except ImportError:
    from http.client import CannotSendRequest
try:
    from stem.process import launch_tor_with_config
except ImportError as err:
    pass

MAX_FIXTURE_TRIES = 3


class TorBrowserDriverFixture(TorBrowserDriver):
    """Extend TorBrowserDriver to have fixtures for tests."""
    def __init__(self, *args, **kwargs):
        self.change_default_tor_cfg(kwargs)
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                return super(TorBrowserDriverFixture, self).__init__(*args,
                                                                     **kwargs)
            except (TimeoutException, WebDriverException) as last_err:
                print ("\nTBDriver init timed out. Attempt %s %s" %
                       ((tries + 1), last_err))
                super(TorBrowserDriverFixture, self).quit()  # clean up
                continue
        else:
            raise TorBrowserDriverInitError("Cannot initialize")

    def change_default_tor_cfg(self, kwargs):
        """Use system Tor if the caller doesn't specifically wants
        to launch a new TBB Tor.

        This makes tests faster and more robust against network
        issues since otherwise we'd have to launch a new Tor process
        for each test.
        """

        if kwargs.get("tor_cfg") != cm.LAUNCH_NEW_TBB_TOR and\
                is_connectable(cm.DEFAULT_SOCKS_PORT):
            kwargs["tor_cfg"] = cm.USE_RUNNING_TOR
            # print ("Will use system Tor for the test")

    def load_url_ensure(self, *args, **kwargs):
        """Make sure the requested URL is loaded. Retry if necessary."""
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                self.load_url(*args, **kwargs)
                if self.current_url != "about:newtab" and \
                        not self.is_connection_error_page:
                    break
            except (TimeoutException,
                    CannotSendRequest) as last_err:
                print ("\nload_url timed out.  Attempt %s %s" %
                       ((tries + 1), last_err))
                continue
        else:
            raise WebDriverException("Can't load the page")


def launch_tor_with_config_fixture(*args, **kwargs):
    for tries in range(MAX_FIXTURE_TRIES):
        try:
            return launch_tor_with_config(*args, **kwargs)
        except OSError as last_err:
            print ("\nlaunch_tor try %s %s" % ((tries + 1), last_err))
            if "timeout without success" in str(last_err):
                continue
            else:
                raise
    raise StemLaunchError("Cannot start Tor")
